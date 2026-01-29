from django.forms import ValidationError
from django.shortcuts import render

# Create your views here.


from masters.models import MainCategory, product_category, product_subcategory
from users.models import *

from rest_framework import viewsets, permissions
from vendor.models import *
from vendor.serializers import BannerCampaignSerializer, ReelSerializer, VendorStoreSerializer, coupon_serializer
from .models import *
from .serializers import AddressSerializer, CartSerializer, OrderSerializer

from rest_framework import viewsets, permissions

class CustomerOrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only return orders for the logged-in user
        user = self.request.user
        return Order.objects.prefetch_related('items').filter(user=user).order_by('-id')

    def perform_create(self, serializer):
        # Automatically set the user when saving
        serializer.save(user=self.request.user)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions




from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rest_framework import generics

from rest_framework import filters

       
from rest_framework import generics, mixins, filters


from .serializers import VendorStoreLiteSerializer

class VendorStoreListAPIView(mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             generics.GenericAPIView):
    queryset = vendor_store.objects.filter(is_active=True)
    serializer_class = VendorStoreSerializer  # ✅ USE NEW ONE HERE
    filter_backends = [filters.SearchFilter]
    search_fields = ["user__first_name", "user__last_name", "user__username"]
    lookup_field = "id"

    def get_serializer_context(self):
        return {"request": self.request}  # ✅ needed for following field

    def get(self, request, *args, **kwargs):
        if "id" in kwargs:
            return self.retrieve(request, *args, **kwargs)
        return self.list(request, *args, **kwargs)    # GET /stores/
 


from vendor.models import product
from vendor.serializers import product_serializer
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from vendor.filters import ProductFilter


from django.db.models import Exists, OuterRef, Value, BooleanField


class ListProducts(ListAPIView):
    serializer_class = product_serializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter

    def get_queryset(self):
        user = self.request.user
        qs = product.objects.filter(
            is_active=True,
        )

        # Filter by customer pincode
          # Get pincode from ?pincode=XXXX in URL
        city = user.city

        if city:
            qs = qs.filter(user__coverages__city__code=city)

        # # Annotate favourites
        # if user.is_authenticated:
        #     favs = Favourite.objects.filter(user=user, product=OuterRef('pk'))
        #     qs = qs.annotate(is_favourite=Exists(favs))
        # else:
        #     qs = qs.annotate(is_favourite=Value(False, output_field=BooleanField()))

        return qs.distinct()
    



# class products_details(APIView):
#     """
#     Get details of a single product by ID.
#     """

#     def get(self, request, product_id):
#         try:
#             # Fetch the product by ID
#             product_obj = product.objects.get(id=product_id)

#         except product.DoesNotExist:
#             return Response(
#                 {"error": "Product not found"},
#                 status=status.HTTP_404_NOT_FOUND
#             )

#         # Serialize and return product data
#         serializer = product_serializer(product_obj, context={'request': request})
#         return Response(serializer.data, status=status.HTTP_200_OK)
    
    
from rest_framework import status


class FollowUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        try:
            target_user = User.objects.get(id=user_id)
            if target_user == request.user:
                return Response({"error": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)
            
            obj, created = Follower.objects.get_or_create(user=target_user, follower=request.user)
            if created:
                return Response({"success": True, "message": f"You are now following {target_user.username}"})
            else:
                return Response({"success": True, "message": f"You already follow {target_user.username}"})
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request):
        """Get list of users the current user is following"""
        following = Follower.objects.filter(follower=request.user).select_related("user")
        data = [{"id": f.user.id, "username": f.user.username} for f in following]
        return Response({"following": data})


class UnfollowUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        try:
            target_user = User.objects.get(id=user_id)
            deleted, _ = Follower.objects.filter(user=target_user, follower=request.user).delete()
            if deleted:
                return Response({"success": True, "message": f"You unfollowed {target_user.username}"})
            else:
                return Response({"success": False, "message": f"You were not following {target_user.username}"})
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request):
        """Get list of users who follow the current user"""
        followers = Follower.objects.filter(user=request.user).select_related("follower")
        data = [{"id": f.follower.id, "username": f.follower.username} for f in followers]
        return Response({"followers": data})


class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



from rest_framework.decorators import action
from rest_framework import serializers

from django.db import transaction
import json




class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Cart.objects.filter(user=self.request.user)
            .select_related("product")
        )

    def perform_create(self, serializer):
        product_instance = serializer.validated_data["product"]
        quantity = serializer.validated_data.get("quantity", 1)

        # ✅ Create or update cart item, tracking store
        try:
            from vendor.models import vendor_store as VendorStore
            store = VendorStore.objects.filter(user=product_instance.user).first()
        except Exception:
            store = None

        cart_item, created = Cart.objects.get_or_create(
            user=self.request.user,
            product=product_instance,
            defaults={"quantity": quantity, "store": store},
        )
        if not created:
            cart_item.quantity += quantity
            if cart_item.store_id is None and store is not None:
                cart_item.store = store
            cart_item.save()

        # print features removed

        return cart_item

    # ✅ Clear cart and add new product
    @action(detail=False, methods=["post"])
    @transaction.atomic
    def clear_and_add(self, request):
        """Clears cart and adds new product (supports print job & file uploads)."""
        product_id = request.data.get("product")
        quantity = request.data.get("quantity", 1)

        if not product_id:
            return Response({"error": "product is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product_instance = product.objects.get(pk=product_id)
        except product.DoesNotExist:
            return Response({"error": "Invalid product id."}, status=status.HTTP_404_NOT_FOUND)

        # Clear user's existing cart
        Cart.objects.filter(user=request.user).delete()

        cart_item = Cart.objects.create(user=request.user, product=product_instance, quantity=quantity)

       
        serializer = self.get_serializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=["patch"])
    def update_quantity(self, request, pk=None):
        """Update only the quantity (increase or decrease) of an existing cart item."""
        try:
            cart_item = Cart.objects.get(pk=pk, user=request.user)
        except Cart.DoesNotExist:
            return Response({"error": "Cart item not found."}, status=404)

        new_qty = request.data.get("quantity")
        if not new_qty:
            return Response({"error": "quantity is required."}, status=400)

        new_qty = int(new_qty)
        if new_qty <= 0:
            cart_item.delete()
            return Response({"message": "Item removed from cart"}, status=200)

        cart_item.quantity = new_qty
        cart_item.save()
        return Response({"message": "Quantity updated ✅", "quantity": cart_item.quantity}, status=200)
    

        # ✅ Clear entire cart
    @action(detail=False, methods=["post"])
    def clear_cart(self, request):
        Cart.objects.filter(user=request.user).delete()
        return Response(
            {"message": "Cart cleared successfully ✅"},
            status=status.HTTP_200_OK,
        )

    

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import random



class RandomBannerAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = BannerCampaign.objects.filter(is_approved = True)
        count = qs.count()

        if count == 0:
            return Response({"detail": "No banners available."}, status=404)

        ids = list(qs.values_list("id", flat=True))
        random_ids = random.sample(ids, min(10, len(ids)))
        banners = qs.filter(id__in=random_ids)

        serializer = BannerCampaignSerializer(banners, many=True)
        return Response(serializer.data)


class reelsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        products = Reel.objects.all()
        serializer = ReelSerializer(products, many=True)
        return Response(serializer.data)

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class FavouriteViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"])
    def add(self, request):
        product_id = request.data.get("product_id")
        user = request.user

        fav, created = Favourite.objects.get_or_create(user=user, product_id=product_id)
        if created:
            return Response({"status": "added"}, status=status.HTTP_201_CREATED)
        return Response({"status": "already exists"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def remove(self, request):
        product_id = request.data.get("product_id")
        user = request.user
        Favourite.objects.filter(user=user, product_id=product_id).delete()
        return Response({"status": "removed"}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["get"])
    def my_favourites(self, request):
        favourites = Favourite.objects.filter(user=request.user).select_related('product')
        products = [fav.product for fav in favourites]
        serializer = product_serializer(products, many=True)
        return Response(serializer.data)
    


class FavouriteStoreViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"])
    def add(self, request):
        store_id = request.data.get("store_id")
        user = request.user

        fav, created = FavouriteStore.objects.get_or_create(user=user, store_id=store_id)
        if created:
            return Response({"status": "added"}, status=status.HTTP_201_CREATED)
        return Response({"status": "already exists"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def remove(self, request):
        store_id = request.data.get("store_id")
        user = request.user
        FavouriteStore.objects.filter(user=user, store_id=store_id).delete()
        return Response({"status": "removed"}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["get"])
    def my_favourites(self, request):
        favourites = FavouriteStore.objects.filter(user=request.user).select_related('store')
        stores = [fav.store for fav in favourites]
        serializer = VendorStoreSerializer(stores, many=True)
        return Response(serializer.data)
    




    permission_classes = [IsAuthenticated]

    def get(self, request):
        products = Reel.objects.all()
        serializer = ReelSerializer(products, many=True)
        return Response(serializer.data)


class offersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        products = Reel.objects.all()
        serializer = ReelSerializer(products, many=True)
        return Response(serializer.data)
    




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone


class CartCouponAPIView(APIView):
    """
    GET: List all active coupons for the store of products in the user's cart.
    POST: Apply a coupon to the cart (send "coupon_code" in body).
    """
    permission_classes = [IsAuthenticated]

    def get_cart_user(self, user):
        cart_items = Cart.objects.filter(user=user)
        if not cart_items.exists():
            return None, cart_items
        return cart_items.first().product.user, cart_items


    def get(self, request):
        user, cart_items = self.get_cart_user(request.user)
        if not user:
            return Response({"coupons": []}, status=200)

        now = timezone.now()
        
        coupons = coupon.objects.filter(
            user=user,
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        )

        serializer = coupon_serializer(coupons, many=True)
        return Response({"coupons": serializer.data}, status=200)

    def post(self, request):
        coupon_code = request.data.get("coupon_code")
        if not coupon_code:
            return Response({"error": "coupon_code is required"}, status=status.HTTP_400_BAD_REQUEST)

        user, cart_items = self.get_cart_user(request.user)
        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            coupon_instance = coupon.objects.get(user=user, code=coupon_code, is_active=True)
        except coupon.DoesNotExist:
            return Response({"error": "Invalid or inactive coupon"}, status=status.HTTP_404_NOT_FOUND)

        # Check validity dates
        if coupon_instance.start_date > timezone.now() or coupon_instance.end_date < timezone.now():
            return Response({"error": "Coupon is not valid at this time."}, status=status.HTTP_400_BAD_REQUEST)

        # Only apply discount-type coupons
        if coupon_instance.coupon_type != "discount":
            return Response({"error": "This coupon cannot be applied to cart total."}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate total cart value
        total_cart_amount = sum(item.product.sales_price * item.quantity for item in cart_items)

        # Check minimum purchase condition
        if coupon_instance.min_purchase and total_cart_amount < coupon_instance.min_purchase:
            return Response({
                "error": f"Cart total must be at least {coupon_instance.min_purchase} to use this coupon."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Calculate discount
        discount_amount = 0
        if coupon_instance.type == "percent" and coupon_instance.discount_percentage:
            discount_amount = (total_cart_amount * coupon_instance.discount_percentage) / 100
            if coupon_instance.max_discount:
                discount_amount = min(discount_amount, coupon_instance.max_discount)
        elif coupon_instance.type == "amount" and coupon_instance.discount_amount:
            discount_amount = coupon_instance.discount_amount

        # Ensure discount does not exceed total
        discount_amount = min(discount_amount, total_cart_amount)
        final_total = total_cart_amount - discount_amount

        # Round amounts
        discount_amount = round(discount_amount, 2)
        final_total = round(final_total, 2)

        return Response({
            "detail": f"Coupon '{coupon_instance.code}' applied successfully.",
            "total_cart_amount": total_cart_amount,
            "discount_amount": discount_amount,
            "final_total": final_total,
            "coupon_type": coupon_instance.coupon_type,
            "discount_method": coupon_instance.type,
            "discount_percentage": coupon_instance.discount_percentage,
            "discount_amount_field": coupon_instance.discount_amount,
            "max_discount": coupon_instance.max_discount,
        }, status=status.HTTP_200_OK)
    




from .serializers import *

class SupportTicketViewSet(viewsets.ModelViewSet):
    serializer_class = SupportTicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:  # Admin can see all tickets
            return SupportTicket.objects.all().order_by("-created_at")
        return SupportTicket.objects.filter(user=user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    

    @action(detail=True, methods=["get", "post"], url_path="messages")
    def messages(self, request, pk=None):
        """Handle GET (list) and POST (send) messages for a ticket"""
        ticket = self.get_object()

        if request.method == "GET":
            msgs = ticket.messages.all().order_by("created_at")
            serializer = TicketMessageSerializer(msgs, many=True)
            return Response(serializer.data)

        if request.method == "POST":
            serializer = TicketMessageSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(ticket=ticket, sender=request.user)
            return Response(serializer.data, status=201)




from django.db.models import Q
from .models import product
from .serializers import product_serializer

class ProductSearchAPIView(ListAPIView):
    serializer_class = product_serializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        search_term = self.request.query_params.get("q")  # use ?q=shirt
        qs = product.objects.filter(is_active=True, sale_type__in = ["online", "both"])

         # Filter by customer pincode
          # Get pincode from ?pincode=XXXX in URL
        city = self.request.GET.get("city")

        if city:
            qs = qs.filter(vendor__coverages__city=city)
        user = self.request.user
        # Annotate favourites
        
    
        if search_term:
            qs = qs.filter(
                Q(name__icontains=search_term) |
                Q(brand_name__icontains=search_term) |
                Q(description__icontains=search_term) |
                Q(color__icontains=search_term) |
                Q(size__icontains=search_term) |
                Q(category__name__icontains=search_term) |
                Q(sub_category__name__icontains=search_term)
            )

        if user.is_authenticated:
            favs = Favourite.objects.filter(user=user, product=OuterRef('pk'))
            qs = qs.annotate(is_favourite=Exists(favs))
        else:
            qs = qs.annotate(is_favourite=Value(False, output_field=BooleanField()))

        return qs.distinct()



class StoreBySubCategoryView(APIView):
    """
    Get all vendor stores that have products in a given subcategory.
    """

    def get(self, request, *args, **kwargs):
        subcategory_id = request.query_params.get('subcategory_id')

        if not subcategory_id:
            return Response(
                {"error": "subcategory_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get distinct user IDs who have products in this subcategory
        user_ids = (
            product.objects.filter(sub_category_id=subcategory_id, is_active=True)
            .values_list('user_id', flat=True)
            .distinct()
        )

        # Get all vendor stores of those users
        stores = vendor_store.objects.filter(user_id__in=user_ids, is_active=True).distinct()

        serializer = VendorStoreSerializer(stores, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    


    

class StoreByCategoryView(APIView):
    """
    Get all vendor stores that have products in a given subcategory.
    """

    def get(self, request, *args, **kwargs):
        category_id = request.query_params.get('category_id')

        if not category_id:
            return Response(
                {"error": "category_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get distinct user IDs who have products in this category
        user_ids = (
            product.objects.filter(category_id=category_id, is_active=True)
            .values_list('user_id', flat=True)
            .distinct()
        )

        # Get all vendor stores of those users
        stores = vendor_store.objects.filter(user_id__in=user_ids, is_active=True).distinct()

        serializer = VendorStoreSerializer(stores, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    


from django.db.models import Prefetch
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import time
from django.db import connection

class HomeScreenView(APIView):
    """
    Return for each MainCategory:
      - categories (product_category list)
      - up to 6 random stores that sell products from those categories
      - up to 6 products (full details) from those categories

    Optimizations:
      - prefetch related sets for products (variants, addons, print variants)
      - fetch all reviews for the product batch in a single query and pass via context
      - fetch store list via user ids derived from product batch (fast)
    """

    def get(self, request, *args, **kwargs):
        start_total = time.time()
        response_data = []

        # Prefetch categories (these are product_category linked from MainCategory)
        main_categories = MainCategory.objects.prefetch_related(
            Prefetch('categories', queryset=product_category.objects.only('id', 'name', 'image'))
        ).only('id', 'name')

        for main_cat in main_categories:
            # direct categories under this main category
            categories_qs = main_cat.categories.all()  # already prefetched
            category_ids = list(categories_qs.values_list('id', flat=True))

            # -------------------------
            # Fetch product batch (limit 6) with related prefetches
            # -------------------------
            products_qs = product.objects.filter(
                category_id__in=category_ids,
                is_active=True
            ).select_related(
                'user', 'category', 'sub_category'
            ).prefetch_related(
                'variants',                           # product.variants (if you have related_name 'variants')
                'variants__size',                     # size on variants
                'print_variants',                     # PrintVariant (related_name)
                'customize_print_variants',           # CustomizePrintVariant (related_name)
                'user__vendor_store'                  # prefetch vendor_store of the user
            ).order_by('?')[:6]  # random 6 products for this main category

            products = list(products_qs)  # evaluate

            product_ids = [p.id for p in products]

            # -------------------------
            # Fetch reviews for all products in batch — single query
            # -------------------------
            reviews_map = {}
            if product_ids:
                # Reviews are referenced via order_item__product in your serializer.
                # We fetch reviews that relate to these products in one shot.
                reviews_qs = Review.objects.filter(order_item__product_id__in=product_ids).select_related('order_item', 'user')
                # Serialize them (use existing ReviewSerializer)
                serialized_reviews = ReviewSerializer(reviews_qs, many=True, context={'request': request}).data

                # Build map: product_id -> list of review dicts
                for r in serialized_reviews:
                    # Try to get product_id from nested order_item if serializer provides it,
                    # else attempt to read it from r['order_item']['product'] etc.
                    # This depends on your ReviewSerializer output; adapt if needed.
                    prod_id = None
                    # safe extraction — best-effort
                    try:
                        prod_id = r.get('order_item', {}).get('product')
                    except Exception:
                        prod_id = None

                    # fallback: attempt to read order_item -> id and then map using DB (rare)
                    if not prod_id:
                        # try to pull from related objects on reviews_qs if needed
                        # since serialized_reviews order matches reviews_qs order, we can map by index,
                        # but easier is to re-query minimal mapping from DB (cheap for small batch)
                        pass

                    if prod_id:
                        reviews_map.setdefault(prod_id, []).append(r)

            # -------------------------
            # Stores: determine user_ids from products we fetched (fast)
            # then pick up to 6 random stores for this main category
            # -------------------------
            user_ids = set([p.user_id for p in products if p.user_id])
            stores_qs = vendor_store.objects.filter(user_id__in=user_ids, is_active=True).only('id', 'name', 'profile_image')
            stores_list = list(stores_qs)
            # pick random up to 6
            random_stores = random.sample(stores_list, min(6, len(stores_list)))
            # ✅ Get approved banner campaigns (latest or random as per your choice)
            stores_data = []
            for s in random_stores:
                store_banners = BannerCampaign.objects.filter(
                    user=s.user,   # 🔥 filter only for this store's owner
                    is_approved=True
                ).order_by('-created_at')[:5]

                store_banners_data = [
                    {
                        'id': b.id,
                        'banner_image': b.banner_image.url if b.banner_image else None,
                    } for b in store_banners
                ]

                stores_data.append({
                    'id': s.id,
                    'name': s.name,
                    'profile_image': s.profile_image.url if s.profile_image else None,
                    'banners': store_banners_data  # 🔥 now store-wise banners
                })

            # -------------------------
            # Serialize products using product_serializer but pass reviews_map in context
            # product_serializer must use reviews_map if present to avoid per-object queries
            # -------------------------
            # prepare serializer context
            ser_context = {'request': request, 'reviews_map': reviews_map}

            # Use your existing serializer but because we prefetched related objects, it should not do extra queries
            products_serialized = product_serializer(products, many=True, context=ser_context).data

            # -------------------------
            # build response payload for this main category
            # -------------------------
            response_data.append({
                "main_category_id": main_cat.id,
                "main_category_name": main_cat.name,
                "subcategories": [
                    {"id": c.id, "name": c.name, "image": c.image.url if c.image else None}
                    for c in categories_qs
                ],
                "stores": stores_data,
                "products": products_serialized
            })

        total_ms = (time.time() - start_total) * 1000.0
        # optional: print timings to server console for debug
        print(f"HomeScreenView total time: {total_ms:.2f} ms")

        return Response(response_data, status=status.HTTP_200_OK)



from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
 
class CustomerProductReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def perform_create(self, serializer):
        order_item = serializer.validated_data['order_item']
        user = self.request.user

        # ✅ Block duplicate review
        if Review.objects.filter(order_item=order_item, user=user).exists():
            raise ValidationError("You have already reviewed this product.")

        # ✅ Ensure user actually purchased THIS exact order item
        if order_item.order.user != user:
            raise ValidationError("You can only review products you have purchased.")

        # ✅ Ensure order was delivered before review
        if order_item.status != "delivered":
            raise ValidationError("You can only review after delivery.")

        # ✅ Save safely
        serializer.save(user=user)



from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
        
class ProductRequestViewSet(viewsets.ModelViewSet):
    queryset = ProductRequest.objects.all().order_by("-created_at")
    serializer_class = ProductRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        # Return only requests created by the logged-in user
        return ProductRequest.objects.filter(user=self.request.user).order_by("-created_at")
    


from stream_chat import StreamChat  # ✅ Correct import

import os


from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from stream_chat import StreamChat
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from vendor.models import  vendor_store
from rest_framework.exceptions import ValidationError



class ChatInitAPIView(APIView):
    """
    Single API endpoint to:
    1. Generate a Stream token for the logged-in user
    2. Create or get a direct chat (customer ↔ vendor)
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        api_key = getattr(settings, "STREAM_API_KEY", None)
        api_secret = getattr(settings, "STREAM_API_SECRET", None)
        if not api_key or not api_secret:
            return Response({"error": "Missing Stream API credentials"}, status=500)

        client = StreamChat(api_key=api_key, api_secret=api_secret)

        me = request.user
        user_id = str(me.id)
        app_role = "customer" if getattr(me, "is_customer", False) else ("vendor" if getattr(me, "is_vendor", False) else "user")

        # Create or update the Stream user
        client.upsert_user({
            "id": user_id,
            "name": me.username,
            "role": "user",
            "app_role": app_role,
        })

        # Create Stream token for frontend use
        token = client.create_token(user_id)

        # Optional: handle direct chat creation if other_user_id is provided
        other_user_id = request.data.get("other_user_id")
        channel_data = None

        if other_user_id:
            User = get_user_model()
            other = get_object_or_404(User, id=other_user_id)

            # Allow only customer↔vendor pairs
            is_allowed = (
                (getattr(me, "is_customer", False) and getattr(other, "is_vendor", False)) or
                (getattr(me, "is_vendor", False) and getattr(other, "is_customer", False))
            )
            if not is_allowed:
                return Response({"error": "Only customer↔vendor chats allowed"}, status=403)

            members = [user_id, str(other.id)]
            channel = client.channel("messaging", data={"members": members, "distinct": True})
            resp = channel.create(user_id)
            channel_id = resp.get("channel", {}).get("id")

            channel_data = {
                "channel_id": channel_id,
                "type": "messaging",
                "members": members,
            }

        return Response({
            "user": {
                "id": user_id,
                "username": me.username,
                "role": "user",
                "app_role": app_role,
            },
            "token": token,
            "api_key": api_key,
            "channel": channel_data,  # will be None if other_user_id not provided
        }, status=200)


# class StoreRatingViewSet(viewsets.ModelViewSet):
#     permission_classes = [IsAuthenticated]
#     serializer_class = StoreRatingSerializer

#     def perform_create(self, serializer):
#         vendor_user_id = serializer.validated_data.pop('vendor_user_id', None)
#         if not vendor_user_id:
#             raise ValidationError({"vendor_user_id": "This field is required."})

#         try:
#             store = vendor_store.objects.get(user_id=vendor_user_id)
#         except vendor_store.DoesNotExist:
#             raise ValidationError({"vendor_user_id": "Store not found for this user"})

#         obj, created = StoreRating.objects.get_or_create(
#             user=self.request.user,
#             store=store,
#             defaults={
#                 'rating': serializer.validated_data.get('rating'),
#                 'comment': serializer.validated_data.get('comment'),
#             }
#         )
#         if not created:
#             obj.rating = serializer.validated_data.get('rating')
#             obj.comment = serializer.validated_data.get('comment')
#             obj.save(update_fields=['rating', 'comment', 'created_at'])
#         self._created_instance = obj

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         out = StoreRatingSerializer(self._created_instance)
#         return Response(out.data, status=201)



# class ConfirmPurchaseView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         """
#         Customer confirms purchase for one or more delivered order items.
#         Body can be:
#           - { "order_item_id": 123 }
#           - { "order_item_ids": [123,124] }
#         No OTP verification is required here.
#         """
#         order_item_id = request.data.get("order_item_id")
#         order_item_ids = request.data.get("order_item_ids")

#         # Normalize ids to list
#         ids = []
#         if isinstance(order_item_ids, list) and order_item_ids:
#             ids = order_item_ids
#         elif order_item_id:
#             ids = [order_item_id]
#         else:
#             return Response({"error": "Provide order_item_id or order_item_ids"}, status=status.HTTP_400_BAD_REQUEST)

#         items = list(OrderItem.objects.select_related("order", "product").filter(id__in=ids))
#         found_ids = {i.id for i in items}
#         missing = [i for i in ids if i not in found_ids]
#         if missing:
#             return Response({"error": "Some items not found", "missing_ids": missing}, status=status.HTTP_404_NOT_FOUND)

#         # Ensure all items belong to the same order
#         order_ids = {i.order_id for i in items}
#         if len(order_ids) != 1:
#             return Response({"error": "All items must belong to the same order"}, status=status.HTTP_400_BAD_REQUEST)

#         order = items[0].order
#         # Only order owner can confirm
#         if getattr(order, "user_id", None) != request.user.id:
#             return Response({"error": "Forbidden: only the order owner can confirm"}, status=status.HTTP_403_FORBIDDEN)

#         # Ensure all selected items are delivered
#         not_delivered = [i.id for i in items if i.status != "delivered"]
#         if not_delivered:
#             return Response({"error": "Items must be delivered before approval", "not_delivered_ids": not_delivered}, status=status.HTTP_400_BAD_REQUEST)

#         # Approve all selected items
#         for i in items:
#             i.status = "approved_by_customer"
#             i.save(update_fields=["status"])

#         # Do not clear OTP here; other items may still need confirmation
#         return Response({"message": "Purchase confirmed", "approved_item_ids": list(found_ids)}, status=status.HTTP_200_OK)

from django.conf import settings
from decimal import Decimal
import datetime as dt
import hmac
import hashlib
import json

class OrderPaymentSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Build payment summary for selected order items.
        Query params:
          - order_item_ids: comma-separated IDs, e.g. ?order_item_ids=1,2,3
          - coupon (optional): coupon code to apply
        """
        ids_param = request.query_params.get("order_item_ids", "")
        coupon_code = request.query_params.get("coupon", "").strip()
        try:
            ids = [int(x) for x in ids_param.split(",") if x.strip()]
        except Exception:
            return Response({"error": "Invalid order_item_ids"}, status=400)
        if not ids:
            return Response({"error": "order_item_ids is required"}, status=400)

        items = list(OrderItem.objects.select_related("order", "product", "product__user").filter(id__in=ids, order__user=request.user))
        found_ids = {i.id for i in items}
        missing = [i for i in ids if i not in found_ids]
        if missing:
            return Response({"error": "Some items not found", "missing_ids": missing}, status=404)

        # Ensure all items belong to the same order and same vendor
        order_ids = {i.order_id for i in items}
        if len(order_ids) != 1:
            return Response({"error": "Items must belong to the same order"}, status=400)
        vendor_ids = {getattr(i.product, "user_id", None) for i in items}
        if len(vendor_ids) != 1:
            return Response({"error": "Items must belong to the same vendor"}, status=400)

        subtotal = Decimal("0.00")
        gst_total = Decimal("0.00")
        line_items = []
        for i in items:
            line_total = Decimal(str(i.price)) * i.quantity
            subtotal += line_total
            rate = getattr(i.product, "gst", None)
            if rate is not None:
                try:
                    gst_total += (line_total * Decimal(str(rate))) / Decimal("100")
                except Exception:
                    pass
            line_items.append({
                "order_item_id": i.id,
                "product_id": i.product_id,
                "quantity": i.quantity,
                "unit_price": str(i.price),
                "line_total": str(line_total)
            })

        discount = Decimal("0.00")
        applied_coupon = None
        if coupon_code:
            try:
                from vendor.models import coupon as Coupon
                now = dt.datetime.now(dt.timezone.utc)
                vendor_user_id = next(iter(vendor_ids))
                c = (Coupon.objects
                     .filter(user_id=vendor_user_id, code=coupon_code, is_active=True, start_date__lte=now, end_date__gte=now)
                     .first())
                if c:
                    if c.type == "percent" and c.discount_percentage:
                        discount = (subtotal * Decimal(str(c.discount_percentage))) / Decimal("100")
                    elif c.type == "amount" and c.discount_amount:
                        discount = Decimal(str(c.discount_amount))
                    if c.max_discount:
                        discount = min(discount, Decimal(str(c.max_discount)))
                    if c.min_purchase and subtotal < Decimal(str(c.min_purchase)):
                        discount = Decimal("0.00")  # do not apply
                    if discount > 0:
                        applied_coupon = {"code": c.code, "type": c.type, "discount": str(discount)}
            except Exception:
                pass

        total_payable = subtotal + gst_total - discount
        data = {
            "items": line_items,
            "subtotal": str(subtotal),
            "gst_total": str(gst_total),
            "discount": str(discount),
            "total_payable": str(total_payable),
            "coupon": applied_coupon,
            "currency": "INR",
        }
        return Response(data, status=200)


class CreateRazorpayOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Create a Razorpay order for selected order items.
        Body: { "order_item_ids": [1,2,3], "coupon": "CODE" (optional) }
        Amount is computed server-side (INR, amount in paise).
        """
        try:
            import razorpay  # type: ignore
        except Exception:
            return Response({"error": "razorpay package not installed on server"}, status=500)

        order_item_ids = request.data.get("order_item_ids") or []
        if not isinstance(order_item_ids, list) or not order_item_ids:
            return Response({"error": "order_item_ids must be a non-empty list"}, status=400)
        coupon_code = (request.data.get("coupon") or "").strip()

        # Reuse summary computation via internal call
        summary_request = request._request
        ids_str = ",".join([str(i) for i in order_item_ids])
        summary_request.GET = summary_request.GET.copy()
        summary_request.GET["order_item_ids"] = ids_str
        if coupon_code:
            summary_request.GET["coupon"] = coupon_code
        summary_resp = OrderPaymentSummaryAPIView().get(request)
        if summary_resp.status_code != 200:
            return summary_resp
        summary = summary_resp.data

        # Determine the single parent order id from the items
        items_qs = OrderItem.objects.select_related("order").filter(id__in=order_item_ids, order__user=request.user)
        parent_order_ids = set(items_qs.values_list("order_id", flat=True))
        if len(parent_order_ids) != 1:
            return Response({"error": "order_item_ids must belong to the same order"}, status=400)
        parent_order_id = next(iter(parent_order_ids))

        total_payable = Decimal(summary["total_payable"])
        amount_paise = int((total_payable * 100).quantize(Decimal("1")))

        key_id = getattr(settings, "RAZORPAY_KEY_ID", None)
        key_secret = getattr(settings, "RAZORPAY_KEY_SECRET", None)
        if not key_id or not key_secret:
            return Response({"error": "Missing RAZORPAY_KEY_ID/RAZORPAY_KEY_SECRET in settings"}, status=500)

        client = razorpay.Client(auth=(key_id, key_secret))
        receipt = f"order_{parent_order_id}_{int(dt.datetime.now().timestamp())}"
        try:
            rz_order = client.order.create({
                "amount": amount_paise,
                "currency": "INR",
                "receipt": receipt,
                "notes": {
                    "app_order_id": str(parent_order_id),
                    "paid_item_ids": ids_str,
                    "user_id": str(request.user.id),
                },
                "payment_capture": 1,
            })
        except Exception as e:
            return Response({"error": "Failed to create Razorpay order", "detail": str(e)}, status=502)

        return Response({
            "razorpay_order_id": rz_order.get("id"),
            "amount": rz_order.get("amount"),
            "currency": rz_order.get("currency", "INR"),
            "summary": summary,
            "key_id": key_id,
        }, status=200)





class RazorpayWebhookAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        webhook_secret = getattr(settings, "RAZORPAY_WEBHOOK_SECRET", None)
        if not webhook_secret:
            return Response({"error": "Webhook secret not configured"}, status=500)

        signature = request.headers.get("X-Razorpay-Signature") or request.headers.get("X-RAZORPAY-SIGNATURE")
        body = request.body

        # Verify signature
        expected = hmac.new(
            webhook_secret.encode("utf-8"),
            body,
            hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(expected, signature or ""):
            return Response({"error": "Invalid signature"}, status=400)

        try:
            payload = json.loads(body.decode("utf-8"))
        except Exception:
            return Response({"error": "Invalid JSON"}, status=400)

        event = payload.get("event")
        # We handle payment.captured and order.paid
        order_entity = None
        if event == "payment.captured":
            order_entity = payload.get("payload", {}).get("payment", {}).get("entity", {}).get("order")
        elif event == "order.paid":
            order_entity = payload.get("payload", {}).get("order", {}).get("entity", {})

        app_order_id = None
        if order_entity and isinstance(order_entity, dict):
            notes = order_entity.get("notes") or {}
            app_order_id = notes.get("app_order_id")
            if not app_order_id:
                # Try to parse receipt like 'order_<id>_timestamp'
                receipt = order_entity.get("receipt") or ""
                if receipt.startswith("order_"):
                    try:
                        app_order_id = receipt.split("_")[1]
                    except Exception:
                        app_order_id = None

        if not app_order_id:
            return Response({"detail": "Ignored: app_order_id not found"}, status=200)

        try:
            order = Order.objects.prefetch_related("items").get(id=int(app_order_id))
        except Exception:
            return Response({"detail": "Ignored: app order not found"}, status=200)

        # Mark all items as approved_by_customer upon capture
        for it in order.items.all():
            if it.status != "approved_by_customer":
                it.status = "approved_by_customer"
                it.save(update_fields=["status"])

        # Reflect order state
        order.status = "accepted"
        order.save(update_fields=["status"])

        return Response({"status": "ok"}, status=200)