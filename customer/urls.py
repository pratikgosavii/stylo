from django.urls import path

from .views import *

from django.conf import settings
from django.conf.urls.static import static




from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'customer-order', CustomerOrderViewSet, basename='CustomerOrderViewSet')
router.register(r'address', AddressViewSet, basename='address')
router.register(r'cart', CartViewSet, basename='cart')

router.register(r'customer-product-review', CustomerProductReviewViewSet, basename='customer_review')

router.register(r'favourites', FavouriteViewSet, basename='favourites')
router.register(r'favourites-store', FavouriteStoreViewSet, basename='favourites_store')

router.register("requests", ProductRequestViewSet, basename="product-request")

router.register(r'support/tickets', SupportTicketViewSet, basename='support-ticket')

# router.register(r'store-rating', StoreRatingViewSet, basename='StoreRatingViewSet')


urlpatterns = [

    
path('stores/', VendorStoreListAPIView.as_view(), name='vendor-store-list'),
path('stores/<int:id>/', VendorStoreListAPIView.as_view(), name='vendor-store-detail'),


path('list-products/', ListProducts.as_view(), name='list_products'),
# path('products-details/<product_id>/', products_details.as_view(), name='products_details'),
path('follow/<int:user_id>/', FollowUserAPIView.as_view(), name='follow-user'),
path('unfollow/<int:user_id>/', UnfollowUserAPIView.as_view(), name='unfollow-user'),
path('follow/', FollowUserAPIView.as_view(), name='following-list'),      # GET = who I'm following
path('unfollow/', UnfollowUserAPIView.as_view(), name='followers-list'),  # GET = who follows me

path('vendor-banner/', RandomBannerAPIView.as_view(), name='RandomBannerAPIView'),  # GET = who follows me
path('reels/', reelsView.as_view(), name='reelsView'),
path('reels/<int:reel_id>/like/', ReelLikeAPIView.as_view(), name='reel-like'),
path('reels/<int:reel_id>/comments/', ReelCommentListCreateAPIView.as_view(), name='reel-comments'),
path('reels/<int:reel_id>/comments/<int:comment_id>/', ReelCommentDeleteAPIView.as_view(), name='reel-comment-delete'),
path('offers/', offersView.as_view(), name='offersView'),  # GET = who follows me

path('coupons/', CartCouponAPIView.as_view(), name='CartCouponAPIView'),  # GET = who follows me

path('products/search/', ProductSearchAPIView.as_view(), name='search-products'),

path('stores-by-category/', StoreByCategoryView.as_view(), name='stores-by-category'),
path('sellers-near-you/', SellersNearYouAPIView.as_view(), name='customer-sellers-near-you'),
path('store-near-me/', StoreNearMeAPIView.as_view(), name='store_near_me'),
path('liked-products-and-stores/', LikedProductsAndStoresAPIView.as_view(), name='customer-liked-products-and-stores'),
path('need-products/', NeedProductsAPIView.as_view(), name='need_products'),
path('home/', CustomerHomeScreenAPIView.as_view(), name='customer_home_screen'),
path('top-picks/', TopPicksAPIView.as_view(), name='customer_top_picks'),
path('spotlight-products/', SpotlightProductsAPIView.as_view(), name='customer_spotlight_products'),

path('main-categories/', MainCategoriesListAPIView.as_view(), name='customer_main_categories'),
path('main-categories/<int:main_category_id>/categories-tree/', CategoriesTreeByMainCategoryAPIView.as_view(), name='customer_categories_tree'),
path('categories/', CategoriesListAPIView.as_view(), name='customer_categories'),
path('subcategories/', SubcategoriesListAPIView.as_view(), name='customer_subcategories'),

path('stores-by-subcategory/', StoreBySubCategoryView.as_view(), name='stores-by-subcategory'),



path("stream/chatinit/", ChatInitAPIView.as_view(), name="ChatInitAPIView"),
path("verify-trial-otp/", VerifyTrialOTPAPIView.as_view(), name="customer-verify-trial-otp"),
path("end-trial/", EndTrialAPIView.as_view(), name="customer-end-trial"),
path("orders/<int:order_id>/select-trial-items/", SelectTrialItemsAPIView.as_view(), name="customer-select-trial-items"),
path("orders/<int:order_id>/cancel/", CancelOrderByCustomerAPIView.as_view(), name="customer-cancel-order"),
path("orders/payment-summary/", OrderPaymentSummaryAPIView.as_view(), name="order-payment-summary"),
path("orders/create-razorpay-order/", CreateRazorpayOrderAPIView.as_view(), name="create-razorpay-order"),
path("razorpay/webhook/", RazorpayWebhookAPIView.as_view(), name="razorpay-webhook"),



]  + router.urls

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)