from django.forms import ValidationError
from django.shortcuts import render

# Create your views here.


from masters.models import MainCategory, product_category, product_subcategory
from users.models import *

from rest_framework import viewsets, permissions
from vendor.models import vendor_store
from vendor.models import *
from vendor.serializers import BannerCampaignSerializer, ReelSerializer, VendorStoreSerializer, VendorStoreSerializer2, coupon_serializer, OfferSerializer, StoreOfferSerializer
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
from django.db.models import Case, When, Value, IntegerField

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

    def get_queryset(self):
        qs = vendor_store.objects.filter(is_active=True)
        # Sort by distance (nearby) when user location is available
        user = self.request.user
        user_lat, user_lon = None, None
        if user.is_authenticated:
            default_address_obj = Address.objects.filter(user=user, is_default=True).first()
            if default_address_obj and default_address_obj.latitude is not None and default_address_obj.longitude is not None:
                try:
                    user_lat = float(default_address_obj.latitude)
                    user_lon = float(default_address_obj.longitude)
                except (TypeError, ValueError):
                    pass
        req_lat = self.request.query_params.get("latitude")
        req_lon = self.request.query_params.get("longitude")
        if req_lat is not None and req_lon is not None:
            try:
                user_lat = float(req_lat)
                user_lon = float(req_lon)
            except (TypeError, ValueError):
                pass
        if user_lat is not None and user_lon is not None:
            stores = list(
                vendor_store.objects.filter(
                    is_active=True,
                    latitude__isnull=False,
                    longitude__isnull=False,
                ).only("id", "latitude", "longitude")
            )
            if stores:
                store_distances = []
                for s in stores:
                    try:
                        d = _haversine_km(user_lat, user_lon, float(s.latitude), float(s.longitude))
                    except (TypeError, ValueError):
                        d = 999999
                    store_distances.append((s.id, d))
                store_distances.sort(key=lambda x: x[1])
                ordered_ids = [sid for sid, _ in store_distances]
                whens = [When(id=sid, then=Value(i)) for i, sid in enumerate(ordered_ids)]
                qs = qs.annotate(
                    _nearby_order=Case(*whens, default=Value(999999), output_field=IntegerField())
                ).order_by("_nearby_order", "id")
        return qs

    def get(self, request, *args, **kwargs):
        if "id" in kwargs:
            return self.retrieve(request, *args, **kwargs)
        return self.list(request, *args, **kwargs)    # GET /stores/
 


from vendor.models import product
from vendor.serializers import product_serializer
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from vendor.filters import ProductFilter


from django.db.models import Exists, OuterRef, Value, BooleanField, Case, When, IntegerField, FloatField, Avg
from django.db.models.functions import Coalesce


class ListProducts(ListAPIView):
    """
    GET /customer/list-products/
    Filter params: search, name, brand_name, color, description, batch_number,
    min_price, max_price, min_mrp, max_mrp, min_stock, max_stock, in_stock,
    main_category_id, category_id, sub_category_id, store_id, user_id,
    is_popular, is_featured, is_active,
    ordering: -sales_price (price high to low), sales_price (price low to high),
    -avg_rating (rating high to low), avg_rating (rating low to high),
    name, -created_at, stock, mrp, etc.
    """
    serializer_class = product_serializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ProductFilter
    ordering_fields = ["name", "sales_price", "mrp", "stock", "created_at", "is_popular", "is_featured", "avg_rating"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        qs = product.objects.filter(is_active=True).annotate(
            avg_rating=Coalesce(Avg("items__product_reviews__rating"), Value(0), output_field=FloatField())
        )

        # Order by nearby: use request.user's location (default address or ?latitude=&longitude=)
        user_lat, user_lon = None, None
        default_address_obj = Address.objects.filter(user=user, is_default=True).first()
        if default_address_obj and default_address_obj.latitude is not None and default_address_obj.longitude is not None:
            try:
                user_lat = float(default_address_obj.latitude)
                user_lon = float(default_address_obj.longitude)
            except (TypeError, ValueError):
                pass
        req_lat = self.request.query_params.get("latitude")
        req_lon = self.request.query_params.get("longitude")
        if req_lat is not None and req_lon is not None:
            try:
                user_lat = float(req_lat)
                user_lon = float(req_lon)
            except (TypeError, ValueError):
                pass

        if user_lat is not None and user_lon is not None:
            stores = list(
                vendor_store.objects.filter(
                    is_active=True,
                    latitude__isnull=False,
                    longitude__isnull=False,
                ).only("id", "user_id", "latitude", "longitude")
            )
            if stores:
                store_distances = []
                for s in stores:
                    try:
                        d = _haversine_km(user_lat, user_lon, float(s.latitude), float(s.longitude))
                    except (TypeError, ValueError):
                        d = 999999
                    store_distances.append((s.user_id, d))
                store_distances.sort(key=lambda x: x[1])
                ordered_user_ids = [uid for uid, _ in store_distances]
                whens = [When(user_id=uid, then=Value(i)) for i, uid in enumerate(ordered_user_ids)]
                qs = qs.annotate(
                    _nearby_order=Case(*whens, default=Value(999999), output_field=IntegerField())
                ).order_by("_nearby_order", "id")

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
            .select_related("product", "product__user")
        )

    def list(self, request, *args, **kwargs):
        """Return cart items grouped by store (vendor). GET /customer/cart/"""
        queryset = self.get_queryset().order_by("product__user_id", "id")
        cart_items = list(queryset)
        if not cart_items:
            return Response({"stores": []}, status=status.HTTP_200_OK)

        # Distinct vendor user_ids from cart products
        user_ids = list({getattr(item.product, "user_id", None) for item in cart_items if getattr(item.product, "user_id", None)})
        stores_qs = vendor_store.objects.filter(user_id__in=user_ids, is_active=True)
        store_by_user_id = {s.user_id: s for s in stores_qs}

        # Group cart items by store (product.user_id)
        from collections import defaultdict
        by_store = defaultdict(list)
        for item in cart_items:
            uid = getattr(item.product, "user_id", None)
            by_store[uid].append(item)

        # Build response: list of { store, items } per store
        stores_payload = []
        for uid in user_ids:
            items = by_store.get(uid) or []
            if not items:
                continue
            store = store_by_user_id.get(uid)
            store_data = VendorStoreSerializer2(store).data if store else {"user_id": uid, "name": "Store", "id": None}
            items_data = [CartSerializer(it, context={"request": request}).data for it in items]
            stores_payload.append({"store": store_data, "items": items_data})

        return Response({"stores": stores_payload}, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        product_instance = serializer.validated_data["product"]
        quantity = serializer.validated_data.get("quantity", 1)

        cart_item, created = Cart.objects.get_or_create(
            user=self.request.user,
            product=product_instance,
            defaults={"quantity": quantity},
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return cart_item

    @action(detail=False, methods=["post"])
    @transaction.atomic
    def clear_and_add(self, request):
        """Clears cart and adds new product."""
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
    """
    GET /customer/reels/
    Returns all reels with like_count, comment_count, is_liked, comments (last 10 per reel),
    and 6 featured products from the same store as each reel.
    """
    permission_classes = [IsAuthenticated]
    FEATURED_PRODUCTS_PER_REEL = 6

    def get(self, request):
        from django.db.models import Count
        from .serializers import ReelCommentSerializer

        reels = Reel.objects.select_related("user").all().order_by("-created_at")
        serializer = ReelSerializer(reels, many=True, context={"request": request})
        data = serializer.data

        reel_ids = [r["id"] for r in data]
        if not reel_ids:
            return Response(data)

        # reel_id -> vendor user_id
        reel_user_map = {r.id: r.user_id for r in reels}
        vendor_user_ids = list({uid for uid in reel_user_map.values() if uid})

        # Bulk: 6 featured products per store (vendor)
        products_by_user = {}
        if vendor_user_ids:
            featured_products = (
                product.objects.filter(
                    user_id__in=vendor_user_ids,
                    is_featured=True,
                    is_active=True,
                    parent__isnull=True,
                )
                .select_related("user", "main_category", "category", "sub_category", "size", "color")
                .order_by("?")
            )
            for p in featured_products:
                uid = p.user_id
                if uid not in products_by_user:
                    products_by_user[uid] = []
                if len(products_by_user[uid]) < self.FEATURED_PRODUCTS_PER_REEL:
                    products_by_user[uid].append(p)
            for uid in products_by_user:
                products_by_user[uid] = product_serializer(
                    products_by_user[uid], many=True, context={"request": request}
                ).data

        # Bulk: like count per reel
        like_counts = dict(
            ReelLike.objects.filter(reel_id__in=reel_ids)
            .values("reel_id")
            .annotate(c=Count("id"))
            .values_list("reel_id", "c")
        )
        # Bulk: comment count per reel
        comment_counts = dict(
            ReelComment.objects.filter(reel_id__in=reel_ids)
            .values("reel_id")
            .annotate(c=Count("id"))
            .values_list("reel_id", "c")
        )
        # Bulk: reels liked by current user
        liked_reel_ids = set(
            ReelLike.objects.filter(reel_id__in=reel_ids, user=request.user).values_list("reel_id", flat=True)
        )
        # Last 10 comments per reel
        comments_qs = (
            ReelComment.objects.filter(reel_id__in=reel_ids)
            .select_related("user")
            .order_by("reel_id", "-created_at")
        )
        comments_by_reel = {}
        for c in comments_qs:
            if c.reel_id not in comments_by_reel:
                comments_by_reel[c.reel_id] = []
            if len(comments_by_reel[c.reel_id]) < 10:
                comments_by_reel[c.reel_id].append(c)

        for item in data:
            rid = item["id"]
            item["like_count"] = like_counts.get(rid, 0)
            item["comment_count"] = comment_counts.get(rid, 0)
            item["is_liked"] = rid in liked_reel_ids
            item["comments"] = ReelCommentSerializer(comments_by_reel.get(rid, []), many=True).data
            vendor_id = reel_user_map.get(rid)
            item["featured_products"] = products_by_user.get(vendor_id, [])[:self.FEATURED_PRODUCTS_PER_REEL]

        return Response(data)


class ReelLikeAPIView(APIView):
    """
    POST /customer/reels/<reel_id>/like/ — add like (idempotent).
    DELETE /customer/reels/<reel_id>/like/ — remove like.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, reel_id):
        try:
            reel = Reel.objects.get(id=reel_id)
        except Reel.DoesNotExist:
            return Response({"detail": "Reel not found."}, status=status.HTTP_404_NOT_FOUND)
        _, created = ReelLike.objects.get_or_create(user=request.user, reel=reel)
        like_count = ReelLike.objects.filter(reel=reel).count()
        return Response(
            {"detail": "Liked." if created else "Already liked.", "like_count": like_count},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    def delete(self, request, reel_id):
        try:
            reel = Reel.objects.get(id=reel_id)
        except Reel.DoesNotExist:
            return Response({"detail": "Reel not found."}, status=status.HTTP_404_NOT_FOUND)
        deleted, _ = ReelLike.objects.filter(user=request.user, reel=reel).delete()
        like_count = ReelLike.objects.filter(reel=reel).count()
        return Response(
            {"detail": "Like removed." if deleted else "Was not liked.", "like_count": like_count},
            status=status.HTTP_200_OK,
        )


class ReelCommentListCreateAPIView(APIView):
    """
    GET /customer/reels/<reel_id>/comments/ — list comments for reel.
    POST /customer/reels/<reel_id>/comments/ — add comment. Body: { "text": "..." }
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, reel_id):
        try:
            Reel.objects.get(id=reel_id)
        except Reel.DoesNotExist:
            return Response({"detail": "Reel not found."}, status=status.HTTP_404_NOT_FOUND)
        comments = ReelComment.objects.filter(reel_id=reel_id).select_related("user").order_by("-created_at")
        from .serializers import ReelCommentSerializer
        serializer = ReelCommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, reel_id):
        try:
            reel = Reel.objects.get(id=reel_id)
        except Reel.DoesNotExist:
            return Response({"detail": "Reel not found."}, status=status.HTTP_404_NOT_FOUND)
        text = request.data.get("text") or (request.data.get("comment") and request.data["comment"])
        if not text or not str(text).strip():
            return Response({"detail": "text is required."}, status=status.HTTP_400_BAD_REQUEST)
        from .serializers import ReelCommentSerializer
        serializer = ReelCommentSerializer(data={"text": str(text).strip()}, context={"request": request, "reel": reel})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ReelCommentDeleteAPIView(APIView):
    """
    DELETE /customer/reels/<reel_id>/comments/<comment_id>/
    Delete a comment. Only the comment author can delete.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, reel_id, comment_id):
        try:
            comment = ReelComment.objects.get(id=comment_id, reel_id=reel_id)
        except ReelComment.DoesNotExist:
            return Response({"detail": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)
        if comment.user_id != request.user.id:
            return Response({"detail": "You can only delete your own comment."}, status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
    


def _store_with_products_response(store, request, product_serializer, VendorStoreSerializer):
    """Build response with full store details and store's products (each product includes full store)."""
    if not store:
        return None
    store_data = VendorStoreSerializer(store, context={"request": request}).data
    products_qs = product.objects.filter(user_id=store.user_id, is_active=True, parent__isnull=True).select_related("main_category", "category", "sub_category")[:50]
    products_data = []
    for p in products_qs:
        prod_data = product_serializer(p, context={"request": request}).data
        if isinstance(prod_data, dict):
            prod_data["store"] = store_data
            prod_data["store_name"] = store.name
            prod_data["store_id"] = store.id
        products_data.append(prod_data)
    return {"store": store_data, "products": products_data}


class FavouriteStoreViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"])
    def add(self, request):
        store_id = request.data.get("store_id")
        user = request.user
        if store_id is None:
            return Response({"detail": "store_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            store = vendor_store.objects.get(id=store_id, is_active=True)
        except vendor_store.DoesNotExist:
            return Response({"detail": "Store not found."}, status=status.HTTP_404_NOT_FOUND)

        fav, created = FavouriteStore.objects.get_or_create(user=user, store_id=store_id)
        payload = _store_with_products_response(store, request, product_serializer, VendorStoreSerializer)
        payload["status"] = "added" if created else "already exists"
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(payload, status=status_code)

    @action(detail=False, methods=["post"])
    def remove(self, request):
        store_id = request.data.get("store_id")
        user = request.user
        if store_id is None:
            return Response({"detail": "store_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        store = vendor_store.objects.filter(id=store_id).first()
        FavouriteStore.objects.filter(user=user, store_id=store_id).delete()
        payload = {"status": "removed"}
        if store:
            payload["store"] = VendorStoreSerializer(store, context={"request": request}).data
            products_qs = product.objects.filter(user_id=store.user_id, is_active=True, parent__isnull=True).select_related("main_category", "category", "sub_category")[:50]
            products_data = []
            for p in products_qs:
                prod_data = product_serializer(p, context={"request": request}).data
                if isinstance(prod_data, dict):
                    prod_data["store"] = payload["store"]
                    prod_data["store_name"] = store.name
                    prod_data["store_id"] = store.id
                products_data.append(prod_data)
            payload["products"] = products_data
        return Response(payload, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["get"])
    def my_favourites(self, request):
        favourites = FavouriteStore.objects.filter(user=request.user).select_related('store')
        stores = [fav.store for fav in favourites]
        serializer = VendorStoreSerializer(stores, many=True, context={"request": request})
        return Response(serializer.data)


class LikedProductsAndStoresAPIView(APIView):
    """
    GET /customer/liked-products-and-stores/
    Returns both liked products and liked stores in one response.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # Liked products
        product_favs = Favourite.objects.filter(user=user, product__is_active=True).select_related("product")
        products = [fav.product for fav in product_favs]
        liked_products = product_serializer(products, many=True, context={"request": request}).data

        # Liked stores
        store_favs = FavouriteStore.objects.filter(user=user).select_related("store")
        stores = [fav.store for fav in store_favs]
        liked_stores = VendorStoreSerializer(stores, many=True, context={"request": request}).data

        return Response({
            "liked_products": liked_products,
            "liked_stores": liked_stores,
        }, status=status.HTTP_200_OK)


class NeedProductsAPIView(APIView):
    """
    GET /customer/need-products/?product_id=<id>
    Returns:
      - more_products_from_store: other products from the same store (excluding the given product).
      - you_may_also_like: products from other stores in the same category/main category.
    Each product includes full store details (store, store_name, store_id, distance_km when user address available).
    Query params: product_id (required), limit (optional, default 10 per section).
    """
    permission_classes = [IsAuthenticated]
    DEFAULT_LIMIT = 10

    def get(self, request):
        product_id = request.query_params.get("product_id")
        if not product_id:
            return Response({"detail": "product_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            product_id = int(product_id)
        except (TypeError, ValueError):
            return Response({"detail": "Invalid product_id"}, status=status.HTTP_400_BAD_REQUEST)

        limit = request.query_params.get("limit", self.DEFAULT_LIMIT)
        try:
            limit = min(int(limit), 20)
        except (TypeError, ValueError):
            limit = self.DEFAULT_LIMIT

        from django.db.models import Q
        # Resolve product (use parent if this is a variant so store/category are consistent)
        prod = product.objects.filter(is_active=True).select_related("user", "main_category", "category", "sub_category").filter(
            Q(id=product_id) | Q(parent_id=product_id)
        ).first()
        if not prod:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        # Use root product for store/category
        root = prod.parent if getattr(prod, "parent_id", None) else prod

        def enrich(prod_list, store_by_uid):
            out = []
            for p in prod_list:
                s = store_by_uid.get(p.user_id)
                data = product_serializer(p, context={"request": request}).data
                if isinstance(data, dict):
                    data["store"] = VendorStoreSerializer(s, context={"request": request}).data if s else None
                    data["store_name"] = s.name if s else None
                    data["store_id"] = s.id if s else None
                    if request.user.is_authenticated and s and s.latitude is not None and s.longitude is not None:
                        addr = Address.objects.filter(user=request.user, is_default=True).first()
                        if addr and addr.latitude is not None and addr.longitude is not None:
                            data["distance_km"] = _haversine_km(
                                float(addr.latitude), float(addr.longitude),
                                float(s.latitude), float(s.longitude)
                            )
                        else:
                            data["distance_km"] = None
                    else:
                        data["distance_km"] = None
                out.append(data)
            return out

        # Store lookup for other stores (for you_may_also_like)
        vendor_user_ids = set()
        more_qs = product.objects.filter(
            user_id=root.user_id, is_active=True, parent__isnull=True
        ).exclude(id=root.id).select_related("user", "main_category", "category", "sub_category").order_by("?")[:limit]
        you_like_qs = product.objects.filter(
            is_active=True, parent__isnull=True
        ).exclude(user_id=root.user_id)
        if root.main_category_id:
            you_like_qs = you_like_qs.filter(main_category_id=root.main_category_id)
        elif root.category_id:
            you_like_qs = you_like_qs.filter(category_id=root.category_id)
        you_like_qs = you_like_qs.select_related("user", "main_category", "category", "sub_category").order_by("?")[:limit]

        for p in more_qs:
            vendor_user_ids.add(p.user_id)
        for p in you_like_qs:
            vendor_user_ids.add(p.user_id)
        vendor_user_ids.add(root.user_id)
        stores_list = list(vendor_store.objects.filter(user_id__in=vendor_user_ids, is_active=True))
        store_by_uid = {s.user_id: s for s in stores_list}

        more_products_from_store = enrich(list(more_qs), store_by_uid)
        you_may_also_like = enrich(list(you_like_qs), store_by_uid)

        return Response({
            "more_products_from_store": more_products_from_store,
            "you_may_also_like": you_may_also_like,
        }, status=status.HTTP_200_OK)


class offersView(APIView):
    """GET: List active store offers (promotional: discount %, free delivery, etc.) currently valid for the customer."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.utils import timezone as tz
        from django.db.models import Q
        from vendor.models import StoreOffer
        today = tz.now().date()
        # Active store offers valid today (valid_from <= today, valid_to >= today or null)
        offers_qs = StoreOffer.objects.filter(
            is_active=True
        ).filter(
            Q(valid_from__isnull=True) | Q(valid_from__lte=today)
        ).filter(
            Q(valid_to__isnull=True) | Q(valid_to__gte=today)
        ).prefetch_related("applicable_products", "applicable_categories").order_by("-created_at")
        serializer = StoreOfferSerializer(offers_qs, many=True, context={"request": request})
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
    GET /customer/stores-by-subcategory/?subcategory_id=<id>
    Returns all vendor stores that have (active) products in the given subcategory.
    """
    permission_classes = [IsAuthenticated]

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
    GET /customer/stores-by-category/?category_id=<id>
    Returns all vendor stores that have (active) products in the given category.
    """
    permission_classes = [IsAuthenticated]

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


class SellersNearYouAPIView(APIView):
    """
    GET /customer/sellers-near-you/
    Returns stores (sellers) within 10km of user, filtered by main_category_id and/or category_id.
    Query params: latitude, longitude (optional; else uses default address), main_category_id, category_id
    """
    permission_classes = [IsAuthenticated]
    NEARBY_KM = 10

    def get(self, request):
        main_category_id = request.query_params.get("main_category_id")
        category_id = request.query_params.get("category_id")
        req_lat = request.query_params.get("latitude")
        req_lon = request.query_params.get("longitude")

        # User location: query params or default address
        user_lat, user_lon = None, None
        default_address_obj = Address.objects.filter(user=request.user, is_default=True).first()
        if default_address_obj and default_address_obj.latitude is not None and default_address_obj.longitude is not None:
            try:
                user_lat = float(default_address_obj.latitude)
                user_lon = float(default_address_obj.longitude)
            except (TypeError, ValueError):
                pass
        if req_lat is not None and req_lon is not None:
            try:
                user_lat = float(req_lat)
                user_lon = float(req_lon)
            except (TypeError, ValueError):
                pass

        # Filter stores by category: only stores that have products in main_category and/or category
        product_qs = product.objects.filter(is_active=True)
        if main_category_id:
            try:
                product_qs = product_qs.filter(category__main_category_id=int(main_category_id))
            except (TypeError, ValueError):
                pass
        if category_id:
            try:
                product_qs = product_qs.filter(category_id=int(category_id))
            except (TypeError, ValueError):
                pass
        vendor_user_ids = list(product_qs.values_list("user_id", flat=True).distinct())

        # Stores that have products in the filtered category
        stores_qs = vendor_store.objects.filter(
            is_active=True,
            user_id__in=vendor_user_ids,
            latitude__isnull=False,
            longitude__isnull=False,
        ).only("id", "user_id", "name", "profile_image", "banner_image", "latitude", "longitude")
        stores_list = list(stores_qs)

        # Filter to within 10km and add distance
        results = []
        for s in stores_list:
            dist = _haversine_km(user_lat or 0, user_lon or 0, float(s.latitude), float(s.longitude))
            if user_lat is not None and user_lon is not None and dist <= self.NEARBY_KM:
                store_data = VendorStoreSerializer(s, context={"request": request}).data
                if isinstance(store_data, dict):
                    store_data["distance_km"] = dist
                results.append(store_data)
        results.sort(key=lambda x: x.get("distance_km", 999999))

        return Response({"stores": results}, status=status.HTTP_200_OK)


from django.db.models import Prefetch
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import time
import math
from django.db import connection


def _haversine_km(lat1, lon1, lat2, lon2):
    """Return distance in km between two (lat, lon) points. Inputs can be float or Decimal."""
    lat1, lon1, lat2, lon2 = float(lat1), float(lon1), float(lat2), float(lon2)
    R = 6371  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)


class CustomerHomeScreenAPIView(APIView):
    """
    Single API for customer home screen UI:
    - Stores nearby: only within 10km of user location
    - All product/banner/offer data from stores within 10km
    - Sections (10 each): banners, random_products, favourite_products, top_picks, offers, featured_products

    Query params:
    - latitude, longitude (optional; if omitted, uses user's default address for distance)
    - main_category_id (optional): filter products/categories by main category

    Logic:
    - Stores: only within 10km of user location
    - All product/banner/offer data filtered by stores within 10km
    - Each section limited to 10 items
    """
    permission_classes = [IsAuthenticated]
    NEARBY_KM = 10
    SECTION_LIMIT = 10

    def get(self, request, *args, **kwargs):
        user = request.user
        req_lat = request.query_params.get("latitude")
        req_lon = request.query_params.get("longitude")
        main_category_id = request.query_params.get("main_category_id")

        # User location: query params or default address (required for 10km filter)
        user_lat, user_lon = None, None
        default_address = None
        default_address_obj = Address.objects.filter(user=user, is_default=True).first()
        if default_address_obj:
            default_address = {
                "id": default_address_obj.id,
                "full_address_text": default_address_obj.full_address,
                "latitude": str(default_address_obj.latitude),
                "longitude": str(default_address_obj.longitude),
            }
            user_lat = float(default_address_obj.latitude)
            user_lon = float(default_address_obj.longitude)
        if req_lat is not None and req_lon is not None:
            try:
                user_lat = float(req_lat)
                user_lon = float(req_lon)
            except (TypeError, ValueError):
                pass

        # Stores nearby: only within 10km
        stores_qs = vendor_store.objects.filter(
            is_active=True, latitude__isnull=False, longitude__isnull=False
        ).only("id", "user_id", "name", "profile_image", "banner_image", "latitude", "longitude")
        stores_list = list(stores_qs)
        stores_nearby = []
        vendor_user_ids = []
        for s in stores_list:
            dist = _haversine_km(user_lat or 0, user_lon or 0, float(s.latitude), float(s.longitude))
            if user_lat is not None and user_lon is not None and dist <= self.NEARBY_KM:
                vendor_user_ids.append(getattr(s, "user_id", None))
                item = {
                    "id": s.id,
                    "user_id": getattr(s, "user_id", None),
                    "name": s.name,
                    "profile_image": request.build_absolute_uri(s.profile_image.url) if s.profile_image else None,
                    "banner_image": request.build_absolute_uri(s.banner_image.url) if s.banner_image else None,
                    "latitude": str(s.latitude),
                    "longitude": str(s.longitude),
                    "distance_km": dist,
                }
                stores_nearby.append(item)
        stores_nearby.sort(key=lambda x: x["distance_km"])
        stores_nearby = stores_nearby[:self.SECTION_LIMIT]
        vendor_user_ids = list({uid for uid in vendor_user_ids if uid is not None})
        if not vendor_user_ids and stores_list:
            store_user_ids = {getattr(s, "user_id", None) for s in stores_list}
            vendor_user_ids = [uid for uid in store_user_ids if uid is not None]

        # Product filter: active products from stores within 10km
        product_filter = product.objects.filter(is_active=True, user_id__in=vendor_user_ids)
        if main_category_id:
            try:
                product_filter = product_filter.filter(main_category_id=int(main_category_id))
            except (TypeError, ValueError):
                pass

        # User greeting
        user_name = (user.first_name or user.last_name or "Customer").strip() or "Customer"
        user_greeting = {"name": user_name, "greeting": f"Hello, {user_name}"}

        store_by_user_id = {s.user_id: s for s in stores_list if getattr(s, "user_id", None)}

        # Categories (filter by main_category_id when provided)
        categories_qs = product_category.objects.only("id", "name", "image", "main_category_id")
        if main_category_id:
            try:
                categories_qs = categories_qs.filter(main_category_id=int(main_category_id))
            except (TypeError, ValueError):
                pass
        categories_qs = categories_qs[:15]
        categories = [
            {"id": c.id, "name": c.name, "image": request.build_absolute_uri(c.image.url) if c.image else None}
            for c in categories_qs
        ]

        # Main categories
        main_categories = [{"id": mc.id, "name": mc.name} for mc in MainCategory.objects.only("id", "name")]

        # Banners: approved BannerCampaign from stores within 10km (limit 10); filter by main_category_id when provided
        banners_qs = BannerCampaign.objects.filter(is_approved=True, user_id__in=vendor_user_ids)
        if main_category_id:
            try:
                banners_qs = banners_qs.filter(main_category_id=int(main_category_id))
            except (TypeError, ValueError):
                pass
        banners_qs = banners_qs.select_related("user").order_by("-created_at")[:self.SECTION_LIMIT]
        banners = []
        for b in banners_qs:
            store = getattr(b.user, "vendor_store", None)
            store_obj = store.first() if store else None
            banners.append({
                "id": b.id,
                "title": b.campaign_name or "",
                "description": "",
                "image": request.build_absolute_uri(b.banner_image.url) if b.banner_image else None,
                "store_id": store_obj.id if store_obj else None,
                "store_name": store_obj.name if store_obj else None,
                "main_category_id": b.main_category_id,
            })

        def _enrich_product(prod, store):
            distance_km = None
            if user_lat is not None and user_lon is not None and store and store.latitude is not None and store.longitude is not None:
                distance_km = _haversine_km(user_lat, user_lon, float(store.latitude), float(store.longitude))
            discount_percent = None
            if prod.mrp and prod.mrp > 0 and prod.sales_price is not None and prod.sales_price < prod.mrp:
                discount_percent = round((float(prod.mrp) - float(prod.sales_price)) / float(prod.mrp) * 100)
            prod_data = product_serializer(prod, context={"request": request}).data
            if isinstance(prod_data, dict):
                prod_data["store_name"] = store.name if store else None
                prod_data["store_id"] = store.id if store else None
                prod_data["distance_km"] = distance_km
                prod_data["discount_percent"] = discount_percent
                # Full store details
                prod_data["store"] = VendorStoreSerializer(store, context={"request": request}).data if store else None
                if prod_data.get("store") and isinstance(prod_data["store"], dict):
                    prod_data["store"]["distance_km"] = distance_km
            return prod_data

        # Random products: 10 random from stores within 10km
        products_random = product_filter.select_related("user", "main_category", "category", "sub_category").order_by("?")[:self.SECTION_LIMIT]
        random_products = [_enrich_product(p, store_by_user_id.get(p.user_id)) for p in products_random]

        # Favourites: 10 user favourites from stores within 10km
        favourites_qs = Favourite.objects.filter(
            user=user, product__user_id__in=vendor_user_ids, product__is_active=True
        ).select_related("product", "product__user", "product__main_category")
        if main_category_id:
            try:
                favourites_qs = favourites_qs.filter(product__main_category_id=int(main_category_id))
            except (TypeError, ValueError):
                pass
        favourites_qs = favourites_qs.order_by("?")[:self.SECTION_LIMIT]
        favourite_products = []
        for fav in favourites_qs:
            p = fav.product
            store = store_by_user_id.get(p.user_id) if p.user_id else None
            favourite_products.append(_enrich_product(p, store))

        # Top picks: 10 products with is_popular from stores within 10km
        products_top_picks = (
            product_filter.filter(is_popular=True)
            .select_related("user", "main_category", "category", "sub_category")
            .order_by("?")[:self.SECTION_LIMIT]
        )
        top_picks = [_enrich_product(p, store_by_user_id.get(p.user_id)) for p in products_top_picks]

        # Featured products: 10 from stores within 10km
        products_featured = (
            product_filter.filter(is_featured=True)
            .select_related("user", "main_category", "category", "sub_category")
            .order_by("?")[:self.SECTION_LIMIT]
        )
        if not products_featured.exists():
            products_featured = (
                product_filter.select_related("user", "main_category", "category", "sub_category")
                .exclude(id__in=[p.get("id") for p in random_products if isinstance(p, dict) and p.get("id")])
                .order_by("?")[:self.SECTION_LIMIT]
            )
        featured_products = [_enrich_product(p, store_by_user_id.get(p.user_id)) for p in products_featured]

        # Offers: store banners (same source as banners; filtered by main_category_id when provided)
        offers = []
        for b in banners_qs:
            store_rel = getattr(b.user, "vendor_store", None)
            store_obj = store_rel.first() if store_rel else None
            offers.append({
                "id": b.id,
                "title": b.campaign_name or "",
                "description": "",
                "image": request.build_absolute_uri(b.banner_image.url) if b.banner_image else None,
                "store_id": store_obj.id if store_obj else None,
                "store_name": store_obj.name if store_obj else None,
                "main_category_id": b.main_category_id,
            })

        payload = {
            "user_greeting": user_greeting,
            "delivery_address": default_address,
            "stores_nearby": stores_nearby,
            "categories": categories,
            "main_categories": main_categories,
            "banners": banners,
            "random_products": random_products,
            "favourite_products": favourite_products,
            "top_picks": top_picks,
            "offers": offers,
            "featured_products": featured_products,
        }
        return Response(payload, status=status.HTTP_200_OK)


class StoreNearMeAPIView(APIView):
    """
    GET /customer/store-near-me/
    Returns stores near the customer within 10km, optionally filtered by main_category and category.
    Query params: main_category (main_category_id), category (category_id), latitude, longitude (optional; else default address).
    """
    permission_classes = [IsAuthenticated]
    NEARBY_KM = 10

    def get(self, request):
        main_category_id = request.query_params.get("main_category")
        category_id = request.query_params.get("category")
        req_lat = request.query_params.get("latitude")
        req_lon = request.query_params.get("longitude")

        user_lat, user_lon = None, None
        default_address_obj = Address.objects.filter(user=request.user, is_default=True).first()
        if default_address_obj and default_address_obj.latitude is not None and default_address_obj.longitude is not None:
            try:
                user_lat = float(default_address_obj.latitude)
                user_lon = float(default_address_obj.longitude)
            except (TypeError, ValueError):
                pass
        if req_lat is not None and req_lon is not None:
            try:
                user_lat = float(req_lat)
                user_lon = float(req_lon)
            except (TypeError, ValueError):
                pass

        product_qs = product.objects.filter(is_active=True)
        if main_category_id:
            try:
                product_qs = product_qs.filter(main_category_id=int(main_category_id))
            except (TypeError, ValueError):
                pass
        if category_id:
            try:
                product_qs = product_qs.filter(category_id=int(category_id))
            except (TypeError, ValueError):
                pass
        vendor_user_ids = list(product_qs.values_list("user_id", flat=True).distinct())

        stores_qs = vendor_store.objects.filter(
            is_active=True,
            user_id__in=vendor_user_ids,
            latitude__isnull=False,
            longitude__isnull=False,
        )
        stores_list = list(stores_qs)

        results = []
        for s in stores_list:
            dist = _haversine_km(user_lat or 0, user_lon or 0, float(s.latitude), float(s.longitude))
            if user_lat is not None and user_lon is not None and dist <= self.NEARBY_KM:
                store_data = VendorStoreSerializer(s, context={"request": request}).data
                if isinstance(store_data, dict):
                    store_data["distance_km"] = dist
                results.append(store_data)
        results.sort(key=lambda x: x.get("distance_km", 999999))

        return Response({"stores": results}, status=status.HTTP_200_OK)


class TopPicksAPIView(APIView):
    """
    GET /customer/top-picks/ — products with is_popular=True.
    Same structure as home top_picks: product data + store_name, store_id, distance_km, discount_percent.
    User location for distance_km comes from request.user's default address. Query params: limit (default 20), offset (default 0).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_lat, user_lon = None, None
        default_address_obj = Address.objects.filter(user=request.user, is_default=True).first()
        if default_address_obj and default_address_obj.latitude is not None and default_address_obj.longitude is not None:
            try:
                user_lat = float(default_address_obj.latitude)
                user_lon = float(default_address_obj.longitude)
            except (TypeError, ValueError):
                pass
        limit = min(int(request.query_params.get("limit", 20)), 100)
        offset = max(0, int(request.query_params.get("offset", 0)))

        stores_list = list(
            vendor_store.objects.filter(is_active=True).only(
                "id", "user_id", "name", "latitude", "longitude"
            )
        )
        store_by_user_id = {s.user_id: s for s in stores_list if getattr(s, "user_id", None)}

        products_top_picks = (
            product.objects.filter(is_active=True, is_popular=True)
            .select_related("user", "category", "sub_category")
            .order_by("-id")[offset : offset + limit]
        )
        top_picks = []
        for p in products_top_picks:
            store = store_by_user_id.get(p.user_id) if p.user_id else None
            distance_km = None
            if user_lat is not None and user_lon is not None and store and store.latitude is not None and store.longitude is not None:
                distance_km = _haversine_km(user_lat, user_lon, float(store.latitude), float(store.longitude))
            discount_percent = None
            if p.mrp and p.mrp > 0 and p.sales_price is not None and p.sales_price < p.mrp:
                discount_percent = round((float(p.mrp) - float(p.sales_price)) / float(p.mrp) * 100)
            prod_data = product_serializer(p, context={"request": request}).data
            if isinstance(prod_data, dict):
                prod_data["store_name"] = store.name if store else None
                prod_data["store_id"] = store.id if store else None
                prod_data["distance_km"] = distance_km
                prod_data["discount_percent"] = discount_percent
            top_picks.append(prod_data)

        return Response({"top_picks": top_picks}, status=status.HTTP_200_OK)


class SpotlightProductsAPIView(APIView):
    """
    GET /customer/spotlight-products/ — spotlight products (vendor-picked) with product data, store_name, store_id, distance_km, discount_tag.
    User location for distance_km from request.user's default address. Query params: limit (default 20), offset (default 0).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from vendor.models import SpotlightProduct

        user = request.user
        user_lat, user_lon = None, None
        default_address_obj = Address.objects.filter(user=user, is_default=True).first()
        if default_address_obj and default_address_obj.latitude is not None and default_address_obj.longitude is not None:
            try:
                user_lat = float(default_address_obj.latitude)
                user_lon = float(default_address_obj.longitude)
            except (TypeError, ValueError):
                pass
        limit = min(int(request.query_params.get("limit", 20)), 100)
        offset = max(0, int(request.query_params.get("offset", 0)))

        stores_list = list(
            vendor_store.objects.filter(is_active=True).only(
                "id", "user_id", "name", "latitude", "longitude"
            )
        )
        store_by_user_id = {s.user_id: s for s in stores_list if getattr(s, "user_id", None)}

        spotlight_qs = (
            SpotlightProduct.objects.filter(product__is_active=True)
            .select_related("product", "user")
            .order_by("-id")[offset : offset + limit]
        )
        results = []
        for sp in spotlight_qs:
            p = sp.product
            store = store_by_user_id.get(p.user_id) if p.user_id else None
            distance_km = None
            if user_lat is not None and user_lon is not None and store and store.latitude is not None and store.longitude is not None:
                distance_km = _haversine_km(user_lat, user_lon, float(store.latitude), float(store.longitude))
            discount_percent = None
            if p.mrp and p.mrp > 0 and p.sales_price is not None and p.sales_price < p.mrp:
                discount_percent = round((float(p.mrp) - float(p.sales_price)) / float(p.mrp) * 100)
            prod_data = product_serializer(p, context={"request": request}).data
            if isinstance(prod_data, dict):
                prod_data["store_name"] = store.name if store else None
                prod_data["store_id"] = store.id if store else None
                prod_data["distance_km"] = distance_km
                prod_data["discount_percent"] = discount_percent
                prod_data["discount_tag"] = sp.discount_tag
                prod_data["spotlight_id"] = sp.id
            results.append(prod_data)

        return Response({"spotlight_products": results}, status=status.HTTP_200_OK)


class MainCategoriesListAPIView(APIView):
    """GET /customer/main-categories/ — list all main categories (id, name)."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = MainCategory.objects.only("id", "name").order_by("name")
        data = [{"id": m.id, "name": m.name} for m in qs]
        return Response(data, status=status.HTTP_200_OK)


class CategoriesListAPIView(APIView):
    """GET /customer/categories/?main_category_id=4 — list categories; filter by main_category_id."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        main_category_id = request.query_params.get("main_category_id")
        qs = product_category.objects.select_related("main_category").only("id", "main_category_id", "name", "image")
        if main_category_id:
            qs = qs.filter(main_category_id=main_category_id)
        data = [
            {
                "id": c.id,
                "main_category_id": c.main_category_id,
                "name": c.name,
                "image": request.build_absolute_uri(c.image.url) if c.image else None,
            }
            for c in qs.order_by("name")
        ]
        return Response(data, status=status.HTTP_200_OK)


class SubcategoriesListAPIView(APIView):
    """GET /customer/subcategories/?category_id=2 — list subcategories; filter by category_id."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        category_id = request.query_params.get("category_id")
        qs = product_subcategory.objects.select_related("category").only("id", "category_id", "name", "image")
        if category_id:
            qs = qs.filter(category_id=category_id)
        data = [
            {
                "id": s.id,
                "category_id": s.category_id,
                "name": s.name,
                "image": request.build_absolute_uri(s.image.url) if s.image else None,
            }
            for s in qs.order_by("name")
        ]
        return Response(data, status=status.HTTP_200_OK)


class CategoriesTreeByMainCategoryAPIView(APIView):
    """
    GET /customer/main-categories/<main_category_id>/categories-tree/
    Returns main category + all categories linked to it + all subcategories linked to those categories.
    Example: main_category_id=4 → main_category (id 4), categories under it, each with subcategories.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, main_category_id):
        main_cat = MainCategory.objects.filter(id=main_category_id).first()
        if not main_cat:
            return Response({"error": "Main category not found."}, status=status.HTTP_404_NOT_FOUND)

        categories_qs = (
            product_category.objects.filter(main_category_id=main_category_id)
            .only("id", "name", "image")
            .order_by("name")
        )
        category_ids = list(categories_qs.values_list("id", flat=True))
        subcategories_qs = (
            product_subcategory.objects.filter(category_id__in=category_ids)
            .only("id", "category_id", "name", "image")
            .order_by("category_id", "name")
        )
        sub_by_cat = {}
        for s in subcategories_qs:
            sub_by_cat.setdefault(s.category_id, []).append({
                "id": s.id,
                "category_id": s.category_id,
                "name": s.name,
                "image": request.build_absolute_uri(s.image.url) if s.image else None,
            })

        categories = []
        for c in categories_qs:
            categories.append({
                "id": c.id,
                "main_category_id": main_category_id,
                "name": c.name,
                "image": request.build_absolute_uri(c.image.url) if c.image else None,
                "subcategories": sub_by_cat.get(c.id, []),
            })

        payload = {
            "main_category": {"id": main_cat.id, "name": main_cat.name},
            "categories": categories,
        }
        return Response(payload, status=status.HTTP_200_OK)


class HomeScreenView(APIView):
    """
    Category-driven home screen: one section per MainCategory with subcategories,
    stores that sell those categories, and products. Also returns user_greeting and
    delivery_address at the top; optional lat/long adds distance_km to stores and products.

    Query params: latitude, longitude (optional; or uses user's default address for distance).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        start_total = time.time()
        user = request.user
        req_lat = request.query_params.get("latitude")
        req_lon = request.query_params.get("longitude")

        # User location for distance_km (same as CustomerHomeScreenAPIView)
        user_lat, user_lon = None, None
        default_address = None
        default_address_obj = Address.objects.filter(user=user, is_default=True).first()
        if default_address_obj:
            default_address = {
                "id": default_address_obj.id,
                "full_address_text": default_address_obj.full_address,
                "latitude": str(default_address_obj.latitude),
                "longitude": str(default_address_obj.longitude),
            }
            user_lat = float(default_address_obj.latitude)
            user_lon = float(default_address_obj.longitude)
        if req_lat is not None and req_lon is not None:
            try:
                user_lat = float(req_lat)
                user_lon = float(req_lon)
            except (TypeError, ValueError):
                pass

        user_name = (user.first_name or user.last_name or "Customer").strip() or "Customer"
        user_greeting = {"name": user_name, "greeting": f"Hello, {user_name}"}

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
                'variants',
                'variants__size',
                'user__vendor_store'
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
            stores_qs = vendor_store.objects.filter(user_id__in=user_ids, is_active=True).only(
                'id', 'user_id', 'name', 'profile_image', 'latitude', 'longitude'
            )
            stores_list = list(stores_qs)
            # pick random up to 6
            random_stores = random.sample(stores_list, min(6, len(stores_list)))
            # ✅ Get approved banner campaigns (latest or random as per your choice)
            stores_data = []
            for s in random_stores:
                store_banners = BannerCampaign.objects.filter(
                    user_id=s.user_id,
                    is_approved=True
                ).order_by('-created_at')[:5]

                store_banners_data = [
                    {
                        'id': b.id,
                        'banner_image': request.build_absolute_uri(b.banner_image.url) if b.banner_image else None,
                    } for b in store_banners
                ]

                distance_km = None
                if user_lat is not None and user_lon is not None and s.latitude is not None and s.longitude is not None:
                    distance_km = _haversine_km(user_lat, user_lon, float(s.latitude), float(s.longitude))

                stores_data.append({
                    'id': s.id,
                    'name': s.name,
                    'profile_image': request.build_absolute_uri(s.profile_image.url) if s.profile_image else None,
                    'latitude': str(s.latitude) if s.latitude else None,
                    'longitude': str(s.longitude) if s.longitude else None,
                    'distance_km': distance_km,
                    'banners': store_banners_data
                })

            # -------------------------
            # Serialize products using product_serializer but pass reviews_map in context
            # -------------------------
            ser_context = {'request': request, 'reviews_map': reviews_map}
            products_serialized = product_serializer(products, many=True, context=ser_context).data

            # Enrich each product with store_name, store_id, distance_km, discount_percent (for UI)
            store_by_user_id = {s.user_id: s for s in stores_list}
            for i, p in enumerate(products):
                store = store_by_user_id.get(p.user_id) if p.user_id else None
                distance_km = None
                if user_lat is not None and user_lon is not None and store and store.latitude is not None and store.longitude is not None:
                    distance_km = _haversine_km(user_lat, user_lon, float(store.latitude), float(store.longitude))
                discount_percent = None
                if p.mrp and p.mrp > 0 and p.sales_price is not None and p.sales_price < p.mrp:
                    discount_percent = round((float(p.mrp) - float(p.sales_price)) / float(p.mrp) * 100)
                if i < len(products_serialized) and isinstance(products_serialized[i], dict):
                    products_serialized[i]["store_name"] = store.name if store else None
                    products_serialized[i]["store_id"] = store.id if store else None
                    products_serialized[i]["distance_km"] = distance_km
                    products_serialized[i]["discount_percent"] = discount_percent

            # -------------------------
            # build response payload for this main category
            # -------------------------
            response_data.append({
                "main_category_id": main_cat.id,
                "main_category_name": main_cat.name,
                "subcategories": [
                    {
                        "id": c.id,
                        "name": c.name,
                        "image": request.build_absolute_uri(c.image.url) if c.image else None,
                    }
                    for c in categories_qs
                ],
                "stores": stores_data,
                "products": products_serialized,
            })

        total_ms = (time.time() - start_total) * 1000.0
        print(f"HomeScreenView total time: {total_ms:.2f} ms")

        payload = {
            "user_greeting": user_greeting,
            "delivery_address": default_address,
            "sections": response_data,
        }
        return Response(payload, status=status.HTTP_200_OK)



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

        # ✅ Ensure order was completed (delivery lives on Order) before review
        if getattr(order_item.order, "status", None) != "completed":
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
from django.utils import timezone


class VerifyTrialOTPAPIView(APIView):
    """
    POST /customer/verify-trial-otp/
    Body: { "order_id": "<order_id string>", "trial_otp": "123456" }
    Customer enters the trial OTP (e.g. received from delivery boy). Verifies OTP and marks order as trial_begin.
    Order must belong to the logged-in customer.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get("order_id")
        trial_otp = request.data.get("trial_otp")

        if not order_id or trial_otp is None or trial_otp == "":
            return Response(
                {"detail": "order_id and trial_otp are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        trial_otp = str(trial_otp).strip()

        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        if order.user_id != request.user.id:
            return Response({"detail": "You can only verify trial OTP for your own order."}, status=status.HTTP_403_FORBIDDEN)

        if not order.trial_otp:
            return Response({"detail": "This order has no trial OTP."}, status=status.HTTP_400_BAD_REQUEST)

        if order.trial_otp != trial_otp:
            return Response({"detail": "Invalid trial OTP."}, status=status.HTTP_400_BAD_REQUEST)

        order.status = "trial_begin"
        order.trial_begins_at = timezone.now()
        order.save(update_fields=["status", "trial_begins_at"])

        return Response(
            {
                "detail": "Trial OTP verified. Order marked as trial begin.",
                "order_id": order.order_id,
                "status": order.status,
                "trial_begins_at": order.trial_begins_at.isoformat() if order.trial_begins_at else None,
            },
            status=status.HTTP_200_OK,
        )


class EndTrialAPIView(APIView):
    """
    POST /customer/end-trial/
    Body: { "order_id": "<order_id string>" }
    Customer ends the trial for their order. Marks order status as trial_ended and sets trial_ends_at.
    Order must belong to the logged-in customer and must be in trial_begin.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get("order_id")

        if not order_id:
            return Response(
                {"detail": "order_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        if order.user_id != request.user.id:
            return Response(
                {"detail": "You can only end trial for your own order."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if order.status != "trial_begin":
            return Response(
                {"detail": "Only orders in trial begin can be ended. Current status: %s" % order.status},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.status = "trial_ended"
        order.trial_ends_at = timezone.now()
        order.save(update_fields=["status", "trial_ends_at"])

        return Response(
            {
                "detail": "Trial ended. Order marked as trial ended.",
                "order_id": order.order_id,
                "status": order.status,
                "trial_ends_at": order.trial_ends_at.isoformat() if order.trial_ends_at else None,
            },
            status=status.HTTP_200_OK,
        )


class SelectTrialItemsAPIView(APIView):
    """
    POST /customer/orders/<order_id>/select-trial-items/
    Body: { 
        "selected_item_ids": [1, 2, 3],
        "cancellation_reasons": {
            "size_doesnt_fit": true/false,
            "color_looks_different": true/false,
            "material_quality_not_expected": true/false,
            "style_doesnt_suit": true/false,
            "other": true/false
        },
        "other_reason": "optional text if other is true"
    }
    
    After trial ends, customer selects which items they want to keep.
    - Selected items → status becomes 'ordered'
    - Unselected items → status becomes 'cancelled' and stock is restored
    - Order status → 'completed'
    
    If NO items are selected (all cancelled), cancellation_reasons is REQUIRED.
    
    Order must be in 'trial_ended' status and belong to the logged-in customer.
    """
    permission_classes = [IsAuthenticated]

    # Valid cancellation reason keys
    VALID_REASONS = [
        "size_doesnt_fit",
        "color_looks_different",
        "material_quality_not_expected",
        "style_doesnt_suit",
        "other"
    ]

    def post(self, request, order_id):
        selected_item_ids = request.data.get("selected_item_ids", [])
        cancellation_reasons = request.data.get("cancellation_reasons", {})
        other_reason = request.data.get("other_reason", "")
        
        if not isinstance(selected_item_ids, list):
            return Response(
                {"error": "selected_item_ids must be a list of item IDs"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            order = Order.objects.prefetch_related("items__product").get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        if order.user_id != request.user.id:
            return Response(
                {"error": "You can only select items for your own order"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if order.status != "trial_ended":
            return Response(
                {"error": f"Can only select items when order is in 'trial_ended' status. Current status: {order.status}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        items = list(order.items.all())
        if not items:
            return Response({"error": "No items in order"}, status=status.HTTP_400_BAD_REQUEST)

        # Convert to set for fast lookup
        selected_ids = set(selected_item_ids)
        
        # If NO items are selected, require cancellation reasons
        if not selected_ids:
            if not cancellation_reasons:
                return Response(
                    {
                        "error": "cancellation_reasons is required when no items are selected",
                        "required_reasons": {
                            "size_doesnt_fit": "Size doesn't fit",
                            "color_looks_different": "Color looks different from photo",
                            "material_quality_not_expected": "Material quality not as expected",
                            "style_doesnt_suit": "Style doesn't suit me",
                            "other": "Other (provide other_reason)"
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            # Validate at least one reason is true
            has_reason = any(cancellation_reasons.get(r, False) for r in self.VALID_REASONS)
            if not has_reason:
                return Response(
                    {
                        "error": "At least one cancellation reason must be true",
                        "required_reasons": {
                            "size_doesnt_fit": "Size doesn't fit",
                            "color_looks_different": "Color looks different from photo",
                            "material_quality_not_expected": "Material quality not as expected",
                            "style_doesnt_suit": "Style doesn't suit me",
                            "other": "Other (provide other_reason)"
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            # If "other" is selected, other_reason text is required
            if cancellation_reasons.get("other", False) and not other_reason.strip():
                return Response(
                    {"error": "other_reason text is required when 'other' reason is selected"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        
        ordered_items = []
        cancelled_items = []
        
        for item in items:
            if item.id in selected_ids:
                # Customer selected this item - mark as ordered
                item.status = "ordered"
                item.save(update_fields=["status"])
                ordered_items.append(item.id)
            else:
                # Customer did not select - mark as cancelled and restore stock
                item.status = "cancelled"
                item.save(update_fields=["status"])
                
                # Restore stock
                p = item.product
                p.stock = (p.stock or 0) + item.quantity
                p.save(update_fields=["stock"])
                
                cancelled_items.append(item.id)

        # Mark order as completed (or cancelled if no items selected)
        if ordered_items:
            order.status = "completed"
        else:
            order.status = "cancelled"
        
        # Save cancellation reasons to order if any items were cancelled
        if cancelled_items and cancellation_reasons:
            order.cancel_size_doesnt_fit = cancellation_reasons.get("size_doesnt_fit", False)
            order.cancel_color_looks_different = cancellation_reasons.get("color_looks_different", False)
            order.cancel_material_quality_not_expected = cancellation_reasons.get("material_quality_not_expected", False)
            order.cancel_style_doesnt_suit = cancellation_reasons.get("style_doesnt_suit", False)
            order.cancel_other = cancellation_reasons.get("other", False)
            if other_reason.strip():
                order.cancel_other_reason = other_reason.strip()
        
        order.save(update_fields=[
            "status",
            "cancel_size_doesnt_fit",
            "cancel_color_looks_different",
            "cancel_material_quality_not_expected",
            "cancel_style_doesnt_suit",
            "cancel_other",
            "cancel_other_reason"
        ])

        # Recalculate totals based on selected items only
        from decimal import Decimal
        new_item_total = Decimal("0.00")
        for item in items:
            if item.id in selected_ids:
                new_item_total += Decimal(str(item.price)) * item.quantity
        
        new_total_amount = new_item_total + order.shipping_fee - order.coupon
        order.item_total = new_item_total
        order.total_amount = new_total_amount
        order.save(update_fields=["item_total", "total_amount"])

        # Build response
        response_data = {
            "detail": "Items selected successfully. Order completed." if ordered_items else "All items cancelled.",
            "ordered_item_ids": ordered_items,
            "cancelled_item_ids": cancelled_items,
        }
        
        # Include cancellation reasons in response if any items were cancelled
        if cancelled_items and cancellation_reasons:
            response_data["cancellation_reasons"] = {
                "size_doesnt_fit": order.cancel_size_doesnt_fit,
                "color_looks_different": order.cancel_color_looks_different,
                "material_quality_not_expected": order.cancel_material_quality_not_expected,
                "style_doesnt_suit": order.cancel_style_doesnt_suit,
                "other": order.cancel_other,
            }
            if order.cancel_other_reason:
                response_data["other_reason"] = order.cancel_other_reason

        from .serializers import OrderSerializer
        response_data["order"] = OrderSerializer(order, context={"request": request}).data
        
        return Response(response_data, status=status.HTTP_200_OK)


class CancelOrderByCustomerAPIView(APIView):
    """
    Customer cancels their own order. Sets all order items to cancelled
    and restores product stock. Cannot cancel after order is completed.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.prefetch_related("items__product").get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        if order.user_id != request.user.id:
            return Response({"error": "You can only cancel your own order"}, status=status.HTTP_403_FORBIDDEN)

        items = list(order.items.all())
        if not items:
            return Response({"error": "No items in order"}, status=status.HTTP_400_BAD_REQUEST)

        if order.status == "completed":
            return Response(
                {"error": "Cannot cancel after order is completed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Item statuses that already mean no stock (do not double-restore)
        REVERSE_STATUSES = {"cancelled", "returned", "replace"}

        for i in items:
            old_status = i.status
            i.status = "cancelled"
            i.save(update_fields=["status"])
            if old_status not in REVERSE_STATUSES:
                p = i.product
                p.stock = (p.stock or 0) + i.quantity
                p.save(update_fields=["stock"])

        order.status = "cancelled"
        order.save(update_fields=["status"])

        from .serializers import OrderSerializer
        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)


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

        # Ensure all items belong to the same order
        order_ids = {i.order_id for i in items}
        if len(order_ids) != 1:
            return Response({"error": "Items must belong to the same order"}, status=400)
        vendor_ids = {getattr(i.product, "user_id", None) for i in items}

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
        # Apply coupon only when all selected items are from a single vendor
        if coupon_code and len(vendor_ids) == 1:
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

        # Reflect order state (accepted/in_transit/delivered live on Order only; OrderItem unchanged)
        order.status = "accepted"
        order.save(update_fields=["status"])

        return Response({"status": "ok"}, status=200)