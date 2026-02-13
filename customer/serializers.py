from rest_framework import serializers
from .models import *



from vendor.serializers import product_serializer

from django.utils import timezone
import datetime




class OrderItemSerializer(serializers.ModelSerializer):
    product_details = product_serializer(source="product", read_only=True)
    is_return_eligible = serializers.SerializerMethodField()
    is_exchange_eligible = serializers.SerializerMethodField()
    is_reviewed = serializers.SerializerMethodField()  # ✅ NEW FIELD
    class Meta:
        model = OrderItem
        fields = [
            'id', 
            'product', 
            'quantity', 
            'product_details',
            'is_return_eligible',
            'is_exchange_eligible',
            'status',
            'tracking_link',
            'is_reviewed'  # ✅ add here also
        ]

        
    def _is_allowed_check(self, obj, return_type):
        """
        Common check:
        - Order completed (delivery lives on Order, not OrderItem)
        - Product allows return/replacement
        - Within 7 days
        - Item not already cancelled
        """
        if getattr(obj.order, 'status', None) != 'completed':
            return False

        product = obj.product
        order_date = obj.order.created_at
        if isinstance(order_date, datetime.date) and not isinstance(order_date, datetime.datetime):
            order_date = datetime.datetime.combine(order_date, datetime.time.min, tzinfo=timezone.get_current_timezone())

        within_7_days = (timezone.now() - order_date).days <= 7
        if not within_7_days:
            return False

        if return_type == 'return' and not getattr(product, 'return_policy', False):
            return False
        if return_type == 'exchange' and not getattr(product, 'replacement', False):
            return False

        # Item must not already be cancelled
        blocked_status = ['cancelled']
        if obj.status in blocked_status:
            return False

        return True

    def get_is_return_eligible(self, obj):
        return self._is_allowed_check(obj, 'return')

    def get_is_exchange_eligible(self, obj):
        return self._is_allowed_check(obj, 'exchange')

    def get_is_reviewed(self, obj):
        request = self.context.get("request")
        if not request or not getattr(request, "user", None):
            return False
        return Review.objects.filter(order_item=obj, user=request.user).exists()
    
    
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"
        read_only_fields = ["user", "created_at", "updated_at"]



from vendor.models import product
import random, string
from django.db.models import Max


from decimal import Decimal
from collections import defaultdict
from users.serializer import UserProfileSerializer

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_details = UserProfileSerializer(source = 'user', read_only=True)
    address_details = AddressSerializer(source="address", read_only = True)

    class Meta:
        model = Order
        fields = "__all__"
        read_only_fields = ["id", "created_at", "items", "item_total", "total_amount", "order_id", 'user_details', 'address_details', 'store_details']
    
    def generate_order_id(self):
        """Generate sequential order_id like SVIND0001, SVIND0002..."""
        last_order = Order.objects.aggregate(max_id=Max("id"))["max_id"]
        next_number = (last_order or 0) + 1
        return f"SVIND{next_number:05d}"  # 5 digits padded with zeros
            
    def create(self, validated_data):
        request = self.context.get("request")
        items_data = request.data.get("items", [])

        # calculate totals
        item_total = Decimal("0.00")
        order_items = []

        for item in items_data:
            product_id = item.get("product")
            quantity = int(item.get("quantity", 1))

            # fetch product
            try:
                product1 = product.objects.get(id=product_id)
            except product.DoesNotExist:
                raise serializers.ValidationError(
                    {"items": [f"Product with id {product_id} does not exist."]}
                )

            unit_price = Decimal(str(product1.sales_price))
            line_total = unit_price * quantity
            item_total += line_total

            order_items.append(
                OrderItem(
                    product=product1,
                    quantity=quantity,
                    price=unit_price,
                )
            )

        # Stock validation: total quantity per product must not exceed available stock
        qty_by_product = defaultdict(int)
        for oi in order_items:
            qty_by_product[oi.product] += oi.quantity
        for prod, qty in qty_by_product.items():
            available = prod.stock if prod.stock is not None else 0
            if available < qty:
                raise serializers.ValidationError(
                    {"items": [f"Product '{prod.name}' has insufficient stock (available: {available}, requested: {qty})."]}
                )

        # generate order_id
        order_id = self.generate_order_id()

        # convert values from validated_data to Decimal safely
        shipping_fee = Decimal(str(validated_data.get("shipping_fee", 0)))
        coupon = Decimal(str(validated_data.get("coupon", 0)))

        # calculate final total
        total_amount = item_total + shipping_fee - coupon

        # set calculated totals in order
        order = Order.objects.create(
            **validated_data,
            order_id=order_id,
            item_total=item_total,
            total_amount=total_amount,
        )

        # Generate 6-digit trial OTP for delivery verification (trial begin)
        import random
        order.trial_otp = str(random.randint(100000, 999999))
        order.save(update_fields=["trial_otp"])

        # bulk create items with linked order
        for oi in order_items:
            oi.order = order
        OrderItem.objects.bulk_create(order_items)

        # Deduct stock for each product
        for prod, qty in qty_by_product.items():
            prod.stock = (prod.stock or 0) - qty
            prod.save(update_fields=["stock"])

        Cart.objects.filter(user=request.user).delete()


        return order

    def update(self, instance, validated_data):
        allowed_fields = ["status", "delivery_boy", "is_paid"]
        for attr, value in validated_data.items():
            if attr in allowed_fields:
                setattr(instance, attr, value)
        instance.save()
        return instance

   


# ---------- Cart ----------
class CartSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=product.objects.filter(is_active=True))
    product_details = product_serializer(source="product", read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "product", "quantity", "product_details"]

    def create(self, validated_data):
        user = self.context["request"].user
        product_instance = validated_data["product"]
        quantity = validated_data.get("quantity", 1)

        cart_item, created = Cart.objects.get_or_create(
            user=user,
            product=product_instance,
            defaults={"quantity": quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

     
        return cart_item



class TicketMessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = TicketMessage
        fields = "__all__"
        read_only_fields = ["id", "sender", "created_at"]


class SupportTicketSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    messages = TicketMessageSerializer(many=True, read_only=True)

    class Meta:
        model = SupportTicket
        fields = "__all__"
        read_only_fields = ["id", "is_admin", "user", "status", "created_at", "updated_at"]


class ReviewSerializer(serializers.ModelSerializer):

    user_details = UserProfileSerializer(source='user', read_only=True)
    photos = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'order_item', 'photo', 'photos', 'is_visible', 'rating', 'comment', 'user_details', 'created_at', 'updated_at']
        read_only_fields = ["user"]

    def get_photos(self, obj):
        """Return list of photo URLs (from ReviewPhoto + legacy photo)."""
        request = self.context.get('request')
        urls = []
        for rp in obj.photos.all().order_by('order', 'id'):
            if rp.image:
                urls.append(request.build_absolute_uri(rp.image.url) if request else rp.image.url)
        if not urls and obj.photo:
            urls.append(request.build_absolute_uri(obj.photo.url) if request else obj.photo.url)
        return urls

from vendor.models import vendor_store

class VendorStoreLiteSerializer(serializers.ModelSerializer):
    following = serializers.SerializerMethodField()

    class Meta:
        model = vendor_store
        fields = [
            "id", "name", "banner_image", "profile_image", "about",'user',
            "is_active", "is_online", "is_open", "following"
        ]

    def get_following(self, obj):
        user = self.context["request"].user
        # ✅ just check if this vendor has this user as follower
        return Follower.objects.filter(user=obj.user, follower=user).exists()




class ProductRequestSerializer(serializers.ModelSerializer):
    from masters.serializers import product_category_serializer, product_subcategory_serializer

    store = serializers.SerializerMethodField()

    user_details = UserProfileSerializer(source = 'user', read_only = True)
    category_details = product_category_serializer(source = 'category', read_only = True)
    sub_category_details = product_subcategory_serializer(source = 'sub_category', read_only = True)
    class Meta:
        model = ProductRequest
        fields = "__all__"
        read_only_fields = ["user", "created_at"]


    def get_store(self, obj):
        try:
            # Assuming one store per user
            store = obj.user.vendor_store.first()  # related_name='vendor_store'
            if store:
                from .serializers import VendorStoreSerializer2
                return VendorStoreSerializer2(store).data
        except:
            return None


class ReelCommentSerializer(serializers.ModelSerializer):
    """Comment on a reel. Used in list/detail."""
    user_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ReelComment
        fields = ["id", "user", "user_name", "reel", "text", "created_at"]
        read_only_fields = ["user", "reel", "created_at"]

    def get_user_name(self, obj):
        if not obj.user:
            return None
        parts = [obj.user.first_name, obj.user.last_name]
        return " ".join(p for p in parts if p).strip() or obj.user.username

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        validated_data["reel"] = self.context.get("reel")
        return super().create(validated_data)