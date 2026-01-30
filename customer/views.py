from django.forms import ValidationError
from django.shortcuts import render

# Create your views here.


from masters.models import MainCategory, product_category, product_subcategory, home_banner
from users.models import *

from rest_framework import viewsets, permissions
from vendor.models import *
from vendor.serializers import BannerCampaignSerializer, ReelSerializer, VendorStoreSerializer, coupon_serializer, OfferSerializer, StoreOfferSerializer
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
from django_filters.rest_framework import DjangoFilterBackend
from vendor.filters import ProductFilter


from django.db.models import Exists, OuterRef, Value, BooleanField, Case, When, IntegerField


class ListProducts(ListAPIView):
    serializer_class = product_serializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter

    def get_queryset(self):
        user = self.request.user
        qs = product.objects.filter(is_active=True)

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
            .select_related("product")
        )

    def perform_create(self, serializer):
        product_instance = serializer.validated_data["product"]
        quantity = serializer.validated_data.get("quantity", 1)

        try:
            from vendor.models import vendor_store as VendorStore
            store = VendorStore.objects.filter(user=product_instance.user).first()
        except Exception:
            store = None

        # Enforce same-store cart: cart may only contain products from one store
        existing_cart = Cart.objects.filter(user=self.request.user).select_related("product").exclude(product=product_instance)
        if existing_cart.exists():
            first_item = existing_cart.first()
            try:
                cart_store = VendorStore.objects.filter(user=first_item.product.user).first()
            except Exception:
                cart_store = getattr(first_item, "store", None)
            new_store = store
            if cart_store is not None and new_store is not None and cart_store.id != new_store.id:
                raise serializers.ValidationError(
                    "Your cart contains products from another store. Clear the cart or complete the order before adding products from a different store."
                )

        cart_item, created = Cart.objects.get_or_create(
            user=self.request.user,
            product=product_instance,
            defaults={"quantity": quantity, "store": store},
        )
        if not created:
            cart_item.quantity += quantity
            if getattr(cart_item, "store_id", None) is None and store is not None:
                cart_item.store = store
            cart_item.save()

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
    """
    GET /customer/reels/
    Returns all reels with like_count, comment_count, is_liked, comments (last 10 per reel).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.db.models import Count
        from .serializers import ReelCommentSerializer

        reels = Reel.objects.all().order_by("-created_at")
        serializer = ReelSerializer(reels, many=True, context={"request": request})
        data = serializer.data

        reel_ids = [r["id"] for r in data]
        if not reel_ids:
            return Response(data)

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
        # Last 10 comments per reel (for list we include count; fetch comments for each reel for response)
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
    - User greeting + default delivery address (with optional distance)
    - Stores nearby (with distance_km, sorted by distance)
    - Categories (for horizontal icons), Main categories (for buttons)
    - Banners (app-level promotional)
    - Top picks (products with is_popular=True; store_name, distance_km, discount_percent)
    - Offers (app-level promotional offers; same source as banners for "Offers" section)
    - Featured products, Featured collection (with store name, distance_km, discount %)
    Query params: latitude, longitude (optional; if omitted, uses user's default address for distance).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        req_lat = request.query_params.get("latitude")
        req_lon = request.query_params.get("longitude")

        # User location: query params or default address
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

        # User greeting
        user_name = (user.first_name or user.last_name or "Customer").strip() or "Customer"
        user_greeting = {"name": user_name, "greeting": f"Hello, {user_name}"}

        # Stores nearby: all active stores with lat/lon; add distance and sort
        stores_qs = vendor_store.objects.filter(is_active=True).only(
            "id", "user_id", "name", "profile_image", "banner_image", "latitude", "longitude"
        )
        stores_list = list(stores_qs)
        stores_nearby = []
        for s in stores_list:
            item = {
                "id": s.id,
                "name": s.name,
                "profile_image": request.build_absolute_uri(s.profile_image.url) if s.profile_image else None,
                "banner_image": request.build_absolute_uri(s.banner_image.url) if s.banner_image else None,
                "latitude": str(s.latitude) if s.latitude else None,
                "longitude": str(s.longitude) if s.longitude else None,
                "distance_km": None,
            }
            if user_lat is not None and user_lon is not None and s.latitude is not None and s.longitude is not None:
                item["distance_km"] = _haversine_km(user_lat, user_lon, float(s.latitude), float(s.longitude))
            stores_nearby.append(item)
        stores_nearby.sort(key=lambda x: (x["distance_km"] is None, x["distance_km"] or 999999))
        stores_nearby = stores_nearby[:20]

        # Categories (product_category for horizontal row: Jackets, Tops, Dresses...)
        categories_qs = product_category.objects.only("id", "name", "image")[:15]
        categories = [
            {
                "id": c.id,
                "name": c.name,
                "image": request.build_absolute_uri(c.image.url) if c.image else None,
            }
            for c in categories_qs
        ]

        # Main categories (for Women's Fashion, Men's Fashion buttons)
        main_categories = [
            {"id": mc.id, "name": mc.name}
            for mc in MainCategory.objects.only("id", "name")
        ]

        # Banners (app-level: home_banner from masters)
        banners_qs = home_banner.objects.filter(is_active=True).order_by("-created_at")[:5]
        banners = [
            {
                "id": b.id,
                "title": b.title or "",
                "description": b.description or "",
                "image": request.build_absolute_uri(b.image.url) if b.image else None,
            }
            for b in banners_qs
        ]

        # Featured products: active products with store + distance + discount
        store_by_user_id = {s.user_id: s for s in stores_list if getattr(s, "user_id", None)}
        products_featured = (
            product.objects.filter(is_active=True)
            .select_related("user", "category", "sub_category")
            .order_by("?")[:12]
        )
        featured_products = []
        for p in products_featured:
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
            featured_products.append(prod_data)

        # Featured collection: second set (e.g. is_featured or another random set)
        products_collection = (
            product.objects.filter(is_active=True, is_featured=True)
            .select_related("user", "category", "sub_category")
            .order_by("?")[:12]
        )
        if not products_collection:
            products_collection = (
                product.objects.filter(is_active=True)
                .select_related("user", "category", "sub_category")
                .exclude(id__in=[p.get("id") for p in featured_products if isinstance(p, dict) and p.get("id")])
                .order_by("?")[:12]
            )
        featured_collection = []
        for p in products_collection:
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
            featured_collection.append(prod_data)

        # Top picks: products marked is_popular (same structure as featured_products)
        products_top_picks = (
            product.objects.filter(is_active=True, is_popular=True)
            .select_related("user", "category", "sub_category")
            .order_by("?")[:10]
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

        # Offers: app-level promotional offers (same as banners for "Offers" section on home)
        offers = [
            {
                "id": b.id,
                "title": b.title or "",
                "description": b.description or "",
                "image": request.build_absolute_uri(b.image.url) if b.image else None,
            }
            for b in banners_qs
        ]

        payload = {
            "user_greeting": user_greeting,
            "delivery_address": default_address,
            "stores_nearby": stores_nearby,
            "categories": categories,
            "main_categories": main_categories,
            "banners": banners,
            "top_picks": top_picks,
            "offers": offers,
            "featured_products": featured_products,
            "featured_collection": featured_collection,
        }
        return Response(payload, status=status.HTTP_200_OK)


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


class CancelOrderByCustomerAPIView(APIView):
    """
    Customer cancels their own order. Sets all order items to cancelled_by_customer
    and restores product stock. Cannot cancel if any item is already delivered.
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

        if any(i.status == "delivered" for i in items):
            return Response(
                {"error": "Cannot cancel after any item is delivered"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        REVERSE_STATUSES = {
            "rejected",
            "cancelled_by_vendor",
            "cancelled_by_customer",
            "returned_by_customer",
            "returned_by_vendor",
        }
        new_status = "cancelled_by_customer"

        for i in items:
            old_status = i.status
            i.status = new_status
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