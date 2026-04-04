from django.urls import path
from .views import (
    DeliveryBoyLoginAPIView,
    AssignedOrdersAPIView,
    StartDeliveryAPIView,
    ConfirmDeliveryByOTPAPIView,
    MarkOrderReachedAPIView,
)

urlpatterns = [
    path("login/", DeliveryBoyLoginAPIView.as_view(), name="deliveryboy-login"),
    path("assigned-orders/", AssignedOrdersAPIView.as_view(), name="deliveryboy-assigned-orders"),
    path("assigned-orders/<int:order_id>/", AssignedOrdersAPIView.as_view(), name="deliveryboy-assigned-order-detail"),
    path("orders/<int:order_id>/start-delivery/", StartDeliveryAPIView.as_view(), name="deliveryboy-start-delivery"),
    path("orders/<int:order_id>/mark-reached/", MarkOrderReachedAPIView.as_view(), name="deliveryboy-mark-reached"),
    path("orders/<int:order_id>/confirm-delivery/", ConfirmDeliveryByOTPAPIView.as_view(), name="deliveryboy-confirm-delivery"),
]
