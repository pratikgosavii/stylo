from django.urls import path

from .views import *

from django.conf import settings
from django.conf.urls.static import static




from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'customer-address', customer_address_ViewSet, basename='pet-test-booking')
router.register(r'company', CompanyViewSet, basename='bann')



urlpatterns = [


    path('add-event/', add_event, name='add_event'),
    path('update-event/<event_id>', update_event, name='update_event'),
    path('delete-event/<event_id>', delete_event, name='delete_event'),
    path('list-event/', list_event, name='list_event'),
    path('get-event/', get_event.as_view(), name='get_event'),

    path("notification-campaigns/<int:pk>/approve/", approve_notification_campaign, name="approve_notification_campaign"),
    path("notification-campaigns/<int:pk>/reject/", reject_notification_campaign, name="reject_notification_campaign"),
    path('list-notification-campaigns/', list_notification_campaigns, name='list_notification_campaigns'),

    path('add-testimonials/', add_testimonials, name='add_testimonials'),  # create or fetch list of admins
    path('update-testimonials/<testimonials_id>', update_testimonials, name='update_testimonials'),  # create or fetch list of admins
    path('list-testimonials/', list_testimonials, name='list_testimonials'),  # create or fetch list of admins
    path('delete-testimonials/<testimonials_id>', delete_testimonials, name='delete_testimonials'),  # create or fetch list of admins
    path('get-testimonials/', get_testimonials.as_view(), name='get_testimonials'), 

    path('add-city/', add_city, name='add_city'),  # create or fetch list of admins
    path('update-city/<city_id>', update_city, name='update_city'),  # create or fetch list of admins
    path('list-city/', list_city, name='list_city'),  # create or fetch list of admins
    path('delete-city/<city_id>', delete_city, name='delete_city'),  # create or fetch list of admins
    path('get-city/', get_city.as_view(), name='get_city'), 

    path('add-product-main-category/', add_product_main_category, name='add_product_main_category'),  # create or fetch list of admins
    path('update-product-main-category/<product_main_category_id>', update_product_main_category, name='update_product_main_category'),  # create or fetch list of admins
    path('list-product-main-category/', list_product_main_category, name='list_product_main_category'),  # create or fetch list of admins
    path('delete-product-main-category/<product_main_category_id>', delete_product_main_category, name='delete_product_main_category'),  # create or fetch list of admins
    path('get-product-main-category/', get_product_main_category.as_view(), name='get_product_main_category'),

    path('add-product-category/', add_product_category, name='add_product_category'),  # create or fetch list of admins
    path('update-product-category/<product_category_id>', update_product_category, name='update_product_category'),  # create or fetch list of admins
    path('list-product-category/', list_product_category, name='list_product_category'),  # create or fetch list of admins
    path('delete-product-category/<product_category_id>', delete_product_category, name='delete_product_category'),  # create or fetch list of admins
    path('get-product-category/', get_product_category.as_view(), name='get_product_category'),
  # create or fetch list of admins

    path('add-product-subcategory/', add_product_subcategory, name='add_product_subcategory'),  # create or fetch list of admins
    path('update-product-subcategory/<product_subcategory_id>', update_product_subcategory, name='update_product_subcategory'),  # create or fetch list of admins
    path('list-product-subcategory/', list_product_subcategory, name='list_product_subcategory'),  # create or fetch list of admins
    path('delete-product-subcategory/<product_subcategory_id>', delete_product_subcategory, name='delete_product_subcategory'),  # create or fetch list of admins
    path('get-product-subcategory/', get_product_subcategory.as_view(), name='get_product_subcategory'),

    path('add-expense-category/', add_expense_category, name='add_expense_category'),  # create or fetch list of admins
    path('update-expense-category/<expense_category_id>', update_expense_category, name='update_expense_category'),  # create or fetch list of admins
    path('list-expense-category/', list_expense_category, name='list_expense_category'),  # create or fetch list of admins
    path('delete-expense-category/<expense_category_id>', delete_expense_category, name='delete_expense_category'),  # create or fetch list of admins
    path('get-expense-category/', get_expense_category.as_view(), name='get_expense_category'),

    # State master CRUD + API
    path('add-state/', add_state, name='add_state'),
    path('update-state/<state_id>', update_state, name='update_state'),
    path('list-state/', list_state, name='list_state'),
    path('delete-state/<state_id>', delete_state, name='delete_state'),
    path('get-state/', get_state.as_view(), name='get_state'),

    path('add-size/', add_size, name='add_size'),  # create or fetch list of admins
    path('update-size/<size_id>', update_size, name='update_size'),  # create or fetch list of admins
    path('list-size/', list_size, name='list_size'),  # create or fetch list of admins
    path('delete-size/<size_id>', delete_size, name='delete_size'),  # create or fetch list of admins
    path('get-size/', get_size.as_view(), name='get_size'),

    # path('add-customer-address/', add_customer_address.as_view(), name='add_customer_address'),  # create or fetch list of admins
    path('update-customer-address/<customer_address_id>', update_customer_address, name='update_customer_address'),  # create or fetch list of admins
    path('list-customer-address/', list_customer_address, name='list_customer_address'),  # create or fetch list of admins
    path('delete-customer-address/<customer_address_id>', delete_customer_address, name='delete_customer_address'),  # create or fetch list of admins
    # path('get-customer-address/', get_customer_address.as_view() , name='get_customer_address '), 

    
    path('add-home-banner/', add_home_banner, name='add_home_banner'),  # create or fetch list of admins
    path('update-home-banner/<home_banner_id>', update_home_banner, name='update_home_banner'),  # create or fetch list of admins
    path('list-home-banner/', list_home_banner, name='list_home_banner'),  # create or fetch list of admins
    path('vendor-list-bannercampaign/', vendor_list_bannercampaign, name='vendor_list_bannercampaign'),  # create or fetch list of admins
    path('approve-bannercampaign/', approve_bannercampaign, name='approve_bannercampaign'),  # create or fetch list of admins
    path('delete-home-banner/<home_banner_id>', delete_home_banner, name='delete_home_banner'),  # create or fetch list of admins
    path('get-home-banner/', get_home_banner, name='get_home_banner'), 

]  + router.urls

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)