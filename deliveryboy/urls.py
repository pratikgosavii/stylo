from django.urls import path
from .views import DeliveryBoyLoginAPIView, AssignedOrdersAPIView, StartDeliveryAPIView

urlpatterns = [
    path("login/", DeliveryBoyLoginAPIView.as_view(), name="deliveryboy-login"),
    path("assigned-orders/", AssignedOrdersAPIView.as_view(), name="deliveryboy-assigned-orders"),
    path("orders/<int:order_id>/start-delivery/", StartDeliveryAPIView.as_view(), name="deliveryboy-start-delivery"),
]
