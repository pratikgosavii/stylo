from django.urls import path

from .views import *
from customer.views import (
    MainCategoriesListAPIView,
    CategoriesTreeByMainCategoryAPIView,
    CategoriesListAPIView,
    SubcategoriesListAPIView,
)

from django.conf import settings
from django.conf.urls.static import static




from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'coupon', CouponViewSet, basename='CouponViewSet')
router.register(r'banner-campaigns', BannerCampaignViewSet, basename='banner-campaign')

router.register(r'reel', ReelViewSet, basename='ReelViewSet')

router.register(r'product', ProductViewSet, basename='product')
router.register(r'store-reviews', StoreReviewViewSet, basename='store-reviews')

router.register(r'deliveryboys', DeliveryBoyViewSet, basename='deliveryboys')

router.register(r'orders', OrderViewSet, basename='orders')

router.register(r'offer', OfferViewSet, basename="offer")
router.register(r'store-offers', StoreOfferViewSet, basename="store-offer")
router.register(r'spotlight-products', SpotlightProductViewSet, basename='spotlight-product')


urlpatterns = [

   
    
    path("vendor-stores/", VendorStoreAPIView.as_view(), name="vendor-store-list"),
    path('main-categories/', MainCategoriesListAPIView.as_view(), name='vendor_main_categories'),
    path('main-categories/<int:main_category_id>/categories-tree/', CategoriesTreeByMainCategoryAPIView.as_view(), name='vendor_categories_tree'),
    path('categories/', CategoriesListAPIView.as_view(), name='vendor_categories'),
    path('subcategories/', SubcategoriesListAPIView.as_view(), name='vendor_subcategories'),
    path("orders/<int:order_id>/assign-delivery-boy/", AssignDeliveryBoyAPIView.as_view(), name="assign-delivery-boy"),
    path("orders/<int:order_id>/accept/", AcceptOrderAPIView.as_view(), name="vendor-accept-order"),
    path("orders/<int:order_id>/reject/", RejectOrderAPIView.as_view(), name="vendor-reject-order"),
    path("orders/<int:order_id>/ready-to-dispatch/", ReadyToDispatchOrderAPIView.as_view(), name="vendor-ready-to-dispatch"),
    path("orders/<int:order_id>/set-status/", CommonOrderStatusUpdateAPIView.as_view(), name="common-order-status-update"),
    path("orders/<int:order_id>/confirm-delivery/", ConfirmDeliveryByOTPAPIView.as_view(), name="confirm-delivery-by-otp"),

    path('add-coupon/', add_coupon, name='add_coupon'),
    path('update-coupon/<coupon_id>', update_coupon, name='update_coupon'),
    path('delete-coupon/<coupon_id>', delete_coupon, name='delete_coupon'),
    path('list-coupon/', list_coupon, name='list_coupon'),

    path('add-bannercampaign/', add_bannercampaign, name='add_bannercampaign'),
    path('update-bannercampaign/<bannercampaign_id>', update_bannercampaign, name='update_bannercampaign'),
    path('delete-bannercampaign/<bannercampaign_id>', delete_bannercampaign, name='delete_bannercampaign'),
    path('list-bannercampaign/', list_bannercampaign, name='list_bannercampaign'),

    path("delivery-boy/login/", DeliveryBoyLoginAPIView.as_view(), name="delivery-boy-login"),
    path("delivery-boy/logout/", DeliveryBoyLogoutAPIView.as_view(), name="delivery-boy-logout"),


]  + router.urls

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)