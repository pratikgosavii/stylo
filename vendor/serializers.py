from customer.models import Review
from rest_framework import serializers
from users.serializer import UserProfileSerializer
from .models import *
from masters.serializers import *



class coupon_serializer(serializers.ModelSerializer):
    class Meta:
        model = coupon
        fields = '__all__'



class BannerCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = BannerCampaign
        fields = '__all__'
        read_only_fields = ['user', 'is_approved', 'created_at']


class ProductGalleryImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductGalleryImage
        fields = ['id', 'image', 'image_url', 'order']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url if obj.image else None


class ProductVariantSerializer(serializers.ModelSerializer):
    size_details = size_serializer(source='size', read_only=True)
    color_details = color_serializer(source='color', read_only=True)
    gallery_images = serializers.SerializerMethodField()

    avg_rating = serializers.SerializerMethodField()    
    reviews = serializers.SerializerMethodField()

    is_favourite = serializers.SerializerMethodField()  # ✅ dynamic now

    class Meta:
        model = product
        fields = '__all__'

    def get_gallery_images(self, obj):
        qs = obj.gallery_images.all().order_by('order', 'id')
        return ProductGalleryImageSerializer(qs, many=True, context=self.context).data

    def _get_reviews_queryset(self, obj):
        """ Reuse same queryset to avoid double DB hit """
        if not hasattr(self, '_cached_reviews'):
            self._cached_reviews = Review.objects.filter(order_item__product=obj)
        return self._cached_reviews

    def get_reviews(self, obj):
        from customer.serializers import ReviewSerializer
        reviews = self._get_reviews_queryset(obj)
        return ReviewSerializer(reviews, many=True).data

    def get_avg_rating(self, obj):
        from django.db.models import Avg
        reviews = self._get_reviews_queryset(obj)
        avg = reviews.aggregate(avg=Avg('rating'))['avg']
        return round(avg, 1) if avg else 0.0
    

    def get_is_favourite(self, obj):
        from customer.models import Favourite

        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False

        # ✅ Cache favourite IDs (only one DB query per request)
        if not hasattr(self, "_user_fav_ids"):
            self._user_fav_ids = set(
                Favourite.objects.filter(user=request.user)
                .values_list("product_id", flat=True)
            )

        return obj.id in self._user_fav_ids


class VendorStoreSerializer2(serializers.ModelSerializer):

    class Meta:
        model = vendor_store
        fields = '__all__'



import json
from rest_framework import serializers

class product_serializer(serializers.ModelSerializer):
    size_details = size_serializer(read_only=True, source='size')
    color_details = color_serializer(read_only=True, source='color')
    gallery_images = serializers.SerializerMethodField()
    is_favourite = serializers.BooleanField(read_only=True)
    # variants = ProductVariantSerializer(many=True, read_only=True)
    variants = serializers.SerializerMethodField()
    store = serializers.SerializerMethodField()

    # Add reviews as nested read-only field
    avg_rating = serializers.SerializerMethodField()    
    reviews = serializers.SerializerMethodField()

    class Meta:
        model = product
        fields = '__all__'

    def get_gallery_images(self, obj):
        qs = obj.gallery_images.all().order_by('order', 'id')
        return ProductGalleryImageSerializer(qs, many=True, context=self.context).data

    def _parse_json_field(self, data, key):
        """
        Safely parse a JSON-like field from request.data for both JSON and form-data:
        - Already parsed lists/objects (application/json) are returned as-is
        - Stringified JSON (form-data Text) is parsed
        - For 'addons', also accept CSV like '14,22'
        """
        value = data.get(key)
        if value is None or value == "":
            return []
        if isinstance(value, (list, dict)):
            return value
        if isinstance(value, str):
            s = value.strip()
            if not s:
                return []
            try:
                return json.loads(s)
            except Exception:
               
                return []
        return []

  
        
    def _get_reviews_queryset(self, obj):
        if not hasattr(self, '_reviews_cache'):
            self._reviews_cache = {}
        if obj.id not in self._reviews_cache:
            self._reviews_cache[obj.id] = Review.objects.filter(order_item__product=obj)
        return self._reviews_cache[obj.id]


    def get_reviews(self, obj):
        from customer.serializers import ReviewSerializer
        reviews = self._get_reviews_queryset(obj)
        return ReviewSerializer(reviews, many=True).data

    def get_avg_rating(self, obj):
        from django.db.models import Avg
        reviews = self._get_reviews_queryset(obj)
        avg = reviews.aggregate(avg=Avg('rating'))['avg']
        return round(avg, 1) if avg else 0.0

    def get_store(self, obj):
        try:
            # Assuming one store per user
            store = obj.user.vendor_store.first()  # related_name='vendor_store'
            if store:
                from .serializers import VendorStoreSerializer2
                return VendorStoreSerializer2(store).data
        except:
            return None
        

    def get_variants(self, obj):
        # Always show full family: root (parent if any) + all its children
        root = obj if getattr(obj, "parent_id", None) is None else obj.parent
        family = [root] + list(root.variants.all())
        # Remove potential duplicates while preserving order
        seen = set()
        unique_family = []
        for p in family:
            if p.id not in seen:
                seen.add(p.id)
                unique_family.append(p)
        serializer = ProductVariantSerializer(unique_family, many=True, context=self.context)
        return serializer.data

class ReelSerializer(serializers.ModelSerializer):

    product_details = product_serializer(source = 'product', read_only = True)
    store = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = Reel
        fields = '__all__'
        read_only_fields = ['user']  


    def get_store(self, obj):
        try:
            # Assuming one store per user
            store = obj.user.vendor_store.first()  # related_name='vendor_store'
            if store:
                from .serializers import VendorStoreSerializer2
                return VendorStoreSerializer2(store).data
        except:
            return None
        
    def get_is_following(self, obj):

        from customer.models import Follower

        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Check if request.user is following obj.user
            return Follower.objects.filter(user=obj.user, follower=request.user).exists()
        return False

    
from django.utils import timezone


class StoreCoverMediaSerializer(serializers.ModelSerializer):
    """Single cover photo or video (image/video file)."""
    media_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = StoreCoverMedia
        fields = ['id', 'store', 'media_type', 'media', 'media_url', 'order', 'created_at']
        read_only_fields = ['store', 'created_at']

    def get_media_url(self, obj):
        request = self.context.get('request')
        if obj.media and request:
            return request.build_absolute_uri(obj.media.url)
        return obj.media.url if obj.media else None


class VendorStoreSerializer(serializers.ModelSerializer):
    # Nested child serializers
    reels = ReelSerializer(source='user.reel_set', many=True, read_only=True)
    banners = BannerCampaignSerializer(source='user.banners', many=True, read_only=True)
    # Single combined list of cover media (photos + videos); each item has media_type
    cover_media = serializers.SerializerMethodField(read_only=True)

    store_rating = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    vendor_name = serializers.SerializerMethodField(read_only=True)
    spotlight_products = serializers.SerializerMethodField(read_only=True)
    featured_products = serializers.SerializerMethodField(read_only=True)
    is_favourite = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = vendor_store
        fields = [
            'id', 'user',
            'vendor_name',
            'name',
            'about',
            'business_type',
            'profile_image',
            'banner_image',
            'cover_media',
            'store_mobile',
            'store_email',
            'house_building_no',
            'locality_street',
            'pincode',
            'state',
            'city',
            'owner_gender',
            'vendor_house_no',
            'vendor_locality_street',

            'vendor_pincode',
            'vendor_state',
            'vendor_city',
            'reels',
            'banners',
            'spotlight_products',
            'featured_products',
            'storetag',
            'latitude',
            'longitude',
            'is_location',
            'is_active',
            'is_online',
            'store_rating',
            'reviews',
            'is_favourite',
        ]

    def get_is_favourite(self, obj):
        """Whether the request user has favourited this store."""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        from customer.models import FavouriteStore
        return FavouriteStore.objects.filter(user=request.user, store=obj).exists()

    def get_vendor_name(self, obj):
        """Vendor/owner name from linked User (first_name + last_name)."""
        if not obj.user:
            return None
        parts = [obj.user.first_name, obj.user.last_name]
        return " ".join(p for p in parts if p).strip() or None

    def get_cover_media(self, obj):
        """Cover photos and videos combined, each item has media_type ('image' or 'video')."""
        qs = obj.cover_media.all().order_by('order', 'id')
        return StoreCoverMediaSerializer(qs, many=True, context=self.context).data

    def get_spotlight_products(self, obj):
        """Spotlight products for this store (via store's user)."""
        if not obj.user:
            return []
        qs = obj.user.spotlight_products.all().select_related('product').order_by('id')
        return SpotlightProductSerializer(qs, many=True, context=self.context).data

    def get_featured_products(self, obj):
        """Products with is_featured=True from this store."""
        if not obj.user:
            return []
        qs = product.objects.filter(user=obj.user, is_featured=True, is_active=True, parent__isnull=True).select_related('category', 'sub_category', 'main_category', 'size', 'color')[:20]
        return ProductVariantSerializer(qs, many=True, context=self.context).data

    def get_store_rating(self, obj):
        """Average product rating for this store (all reviews, visible or not)."""
        try:
            from customer.models import Review
            from django.db.models import Avg
            avg = (Review.objects
                   .filter(order_item__product__user=obj.user)
                   .aggregate(a=Avg('rating'))['a'])
            return round(avg or 0.0, 1)
        except Exception:
            return 0.0

    def get_reviews(self, obj):
        """Return only visible reviews for this store's products."""
        try:
            from customer.models import Review
            from customer.serializers import ReviewSerializer
            qs = Review.objects.filter(order_item__product__user=obj.user, is_visible=True).order_by('-created_at')
            # pass through request if available for nested serializer context
            context = getattr(self, 'context', {})
            return ReviewSerializer(qs, many=True, context=context).data
        except Exception:
            return []

    
class DeliveryBoySerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryBoy
        fields = '__all__'
        read_only_fields = ["user"]   # 👈 Important

    
class OfferSerializer(serializers.ModelSerializer):
    from customer.serializers import ProductRequestSerializer

    seller = serializers.StringRelatedField(read_only=True)
    request_details = ProductRequestSerializer(source = "request", read_only = True)
    seller_user_details = UserProfileSerializer(source = 'seller', read_only = True)
    store = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = "__all__"
        read_only_fields = ["seller", "created_at", "valid_till"]

    def get_store(self, obj):
        try:
            # Assuming one store per user
            store = obj.seller.vendor_store.first()  # related_name='vendor_store'
            if store:
                from .serializers import VendorStoreSerializer2
                return VendorStoreSerializer2(store).data
        except:
            return None


class StoreOfferSerializer(serializers.ModelSerializer):
    """Create Offer form: title, description, offer type (Discount % / Free Delivery), valid from/to, discount value, applicable products/categories, eligibility."""

    offer_type = serializers.SerializerMethodField(read_only=True)
    applicable_products = serializers.PrimaryKeyRelatedField(many=True, queryset=product.objects.all(), required=False, allow_empty=True)
    applicable_categories = serializers.PrimaryKeyRelatedField(many=True, queryset=product_category.objects.all(), required=False, allow_empty=True)

    class Meta:
        model = StoreOffer
        fields = [
            'id', 'user',
            'offer_title', 'offer_description',
            'offer_type', 'is_discount_percent', 'is_free_delivery',
            'valid_from', 'valid_to', 'discount_value',
            'applicable_products', 'applicable_categories',
            'eligibility_criteria', 'is_active', 'created_at',
        ]
        read_only_fields = ['user', 'created_at']

    def get_offer_type(self, obj):
        if obj.is_free_delivery:
            return 'free_delivery'
        if obj.is_discount_percent:
            return 'discount_percent'
        return 'discount_percent'

    def validate(self, attrs):
        offer_type = self.initial_data.get('offer_type')
        if offer_type == 'free_delivery':
            attrs['is_free_delivery'] = True
            attrs['is_discount_percent'] = False
        elif offer_type == 'discount_percent':
            attrs['is_discount_percent'] = True
            attrs['is_free_delivery'] = False
        return attrs

    def create(self, validated_data):
        products = validated_data.pop('applicable_products', [])
        categories = validated_data.pop('applicable_categories', [])
        offer = StoreOffer.objects.create(**validated_data)
        if products:
            offer.applicable_products.set(products)
        if categories:
            offer.applicable_categories.set(categories)
        return offer

    def update(self, instance, validated_data):
        products = validated_data.pop('applicable_products', None)
        categories = validated_data.pop('applicable_categories', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if products is not None:
            instance.applicable_products.set(products)
        if categories is not None:
            instance.applicable_categories.set(categories)
        return instance


class SpotlightProductSerializer(serializers.ModelSerializer):
    """Spotlight product: product + discount_tag for vendor."""
    product_details = product_serializer(source='product', read_only=True)

    class Meta:
        model = SpotlightProduct
        fields = ['id', 'user', 'product', 'product_details', 'discount_tag']
        read_only_fields = ['user']

    def validate_product(self, value):
        # Ensure product belongs to the vendor (request.user)
        request = self.context.get('request')
        if request and value.user_id != request.user.id:
            raise serializers.ValidationError("You can only add your own products to spotlight.")
        return value

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

