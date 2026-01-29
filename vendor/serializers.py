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


class ProductVariantSerializer(serializers.ModelSerializer):
    size_detials = size_serializer(source='size', read_only=True)

    avg_rating = serializers.SerializerMethodField()    
    reviews = serializers.SerializerMethodField()

    is_favourite = serializers.SerializerMethodField()  # ✅ dynamic now

    class Meta:
        model = product
        fields = '__all__'

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

class VendorStoreSerializer(serializers.ModelSerializer):
    # Nested child serializers
    reels = ReelSerializer(source='user.reel_set', many=True, read_only=True)
    banners = BannerCampaignSerializer(source='user.banners', many=True, read_only=True)

    is_store_open = serializers.SerializerMethodField() 
    store_rating = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()

    class Meta:
        model = vendor_store
        fields = [
            'id', 'user',
            'working_hours',
            'spotlight_products',
            'name',
            'about',
            'profile_image',
            'banner_image',
            'reels',
            'banners',
            'storetag',
            'latitude',
            'longitude',
            'is_location',
            'is_active',
            'is_online',
            'is_store_open',
            'is_offline',
            'display_as_catalog',
            'private_catalog',
            'store_rating',
            'reviews',
        ]

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
        
