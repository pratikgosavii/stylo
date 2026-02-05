from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import get_user_model
from vendor.models import DeliveryBoy
from customer.models import Order
from customer.serializers import OrderSerializer

User = get_user_model()


class DeliveryBoyLoginAPIView(APIView):
    """
    POST /deliveryboy/login/
    Body: { "username": "<login_username>", "password": "<password>" }
    Login for delivery boy using the username and password set when vendor added the delivery boy.
    Returns JWT tokens and delivery_boy profile.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        username = (request.data.get("username") or "").strip()
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "username and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Delivery boy account: username is stored in User.mobile when vendor creates delivery boy
        user = User.objects.filter(mobile=username).first()
        if not user or not user.check_password(password):
            return Response(
                {"error": "Invalid username or password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not getattr(user, "is_deliveryboy", False):
            return Response(
                {"error": "Not a delivery boy account"},
                status=status.HTTP_403_FORBIDDEN,
            )

        delivery_boy = DeliveryBoy.objects.filter(account_user=user).first()
        if not delivery_boy:
            return Response(
                {"error": "Not a delivery boy account"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not delivery_boy.is_active:
            return Response(
                {"error": "Delivery boy account is inactive"},
                status=status.HTTP_403_FORBIDDEN,
            )

        refresh = RefreshToken.for_user(user)
        data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "username": username,
                "mobile": user.mobile,
                "email": getattr(user, "email", None),
            },
            "delivery_boy": {
                "id": delivery_boy.id,
                "name": delivery_boy.name,
                "username": delivery_boy.username,
                "mobile": delivery_boy.mobile,
                "email": delivery_boy.email,
            },
        }
        return Response(data, status=status.HTTP_200_OK)


class AssignedOrdersAPIView(APIView):
    """
    GET /deliveryboy/assigned-orders/
    List all orders assigned to the logged-in delivery boy.
    Auth: delivery boy JWT (user.is_deliveryboy).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not getattr(request.user, "is_deliveryboy", False):
            return Response(
                {"error": "Not a delivery boy account"},
                status=status.HTTP_403_FORBIDDEN,
            )
        delivery_boy = DeliveryBoy.objects.filter(account_user=request.user).first()
        if not delivery_boy:
            return Response(
                {"error": "Delivery boy profile not found"},
                status=status.HTTP_403_FORBIDDEN,
            )
        qs = (
            Order.objects.filter(delivery_boy=delivery_boy)
            .prefetch_related("items__product")
            .order_by("-id")
        )
        serializer = OrderSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class StartDeliveryAPIView(APIView):
    """
    POST /deliveryboy/orders/<order_id>/start-delivery/
    Mark order as in_transit (delivery started). Only the assigned delivery boy can call this.
    Auth: delivery boy JWT.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        if not getattr(request.user, "is_deliveryboy", False):
            return Response(
                {"error": "Not a delivery boy account"},
                status=status.HTTP_403_FORBIDDEN,
            )
        delivery_boy = DeliveryBoy.objects.filter(account_user=request.user).first()
        if not delivery_boy:
            return Response(
                {"error": "Delivery boy profile not found"},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            order = Order.objects.prefetch_related("items__product").get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        if not order.delivery_boy or order.delivery_boy.id != delivery_boy.id:
            return Response(
                {"error": "Forbidden: order is not assigned to you"},
                status=status.HTTP_403_FORBIDDEN,
            )
        order.status = "in_transit"
        order.save(update_fields=["status"])
        # Optionally set order items to in_transit
        for item in order.items.all():
            if item.status != "delivered":
                item.status = "in_transit"
                item.save(update_fields=["status"])
        serializer = OrderSerializer(order, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class ConfirmDeliveryAPIView(APIView):
    """
    POST /deliveryboy/orders/<order_id>/confirm-delivery/
    Mark order as reached/delivered. No OTP required.
    Marks all order items as delivered and order as completed.
    Only the assigned delivery boy can call this.
    Auth: delivery boy JWT.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        if not getattr(request.user, "is_deliveryboy", False):
            return Response(
                {"error": "Not a delivery boy account"},
                status=status.HTTP_403_FORBIDDEN,
            )
        delivery_boy = DeliveryBoy.objects.filter(account_user=request.user).first()
        if not delivery_boy:
            return Response(
                {"error": "Delivery boy profile not found"},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            order = Order.objects.prefetch_related("items__product", "delivery_boy").get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        if not order.delivery_boy or order.delivery_boy.id != delivery_boy.id:
            return Response(
                {"error": "Forbidden: order is not assigned to you"},
                status=status.HTTP_403_FORBIDDEN,
            )
        # Mark all items delivered
        for item in order.items.all():
            item.status = "delivered"
            item.save(update_fields=["status"])
        # Complete order
        order.status = "completed"
        order.delivery_otp = None
        order.save(update_fields=["status", "delivery_otp"])
        serializer = OrderSerializer(order, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
