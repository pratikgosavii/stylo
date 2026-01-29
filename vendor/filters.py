import django_filters
from .models import *
from django.db.models import Q

class productFilter(django_filters.FilterSet):

    search = django_filters.CharFilter(method='filter_by_search', label='Search')
    sale_type = django_filters.CharFilter(method='filter_by_sale_type', label='Sale Type')

    class Meta:
        model = product
        exclude = ['image', 'gallery_images', 'user']

    def filter_by_search(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(name__icontains=value) |
                Q(brand_name__icontains=value) |
                Q(hsn__icontains=value)
            )
        return queryset

    def filter_by_sale_type(self, queryset, name, value):
        if value and value.lower() != 'all':
            return queryset.filter(sale_type__iexact=value)
        return queryset
    


class couponFilter(django_filters.FilterSet):
    class Meta:
        model = coupon
        exclude = ['image']  # ⛔ Exclude unsupported field




import django_filters
from .models import product
from users.models import User
from masters.models import product_category, product_subcategory


class ProductFilter(django_filters.FilterSet):

   
    # Text fields with icontains
    name = django_filters.CharFilter(lookup_expr="icontains")
    brand_name = django_filters.CharFilter(lookup_expr="icontains")
    color = django_filters.CharFilter(lookup_expr="icontains")
    size = django_filters.CharFilter(lookup_expr="icontains")
    description = django_filters.CharFilter(lookup_expr="icontains")
    batch_number = django_filters.CharFilter(lookup_expr="icontains")
    hsn = django_filters.CharFilter(lookup_expr="icontains")

    # Price ranges
    min_price = django_filters.NumberFilter(field_name="sales_price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="sales_price", lookup_expr="lte")

    # Expiry date ranges
    expiry_before = django_filters.DateFilter(field_name="expiry_date", lookup_expr="lte")
    expiry_after = django_filters.DateFilter(field_name="expiry_date", lookup_expr="gte")

    # Foreign keys
    user = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    category = django_filters.ModelChoiceFilter(queryset=product_category.objects.all())
    sub_category = django_filters.ModelChoiceFilter(queryset=product_subcategory.objects.all())
    parent = django_filters.ModelChoiceFilter(queryset=product.objects.all())

    # Choice fields

    # Boolean fields
    track_serial_numbers = django_filters.BooleanFilter()
    low_stock_alert = django_filters.BooleanFilter()
    is_customize = django_filters.BooleanFilter()
    instant_delivery = django_filters.BooleanFilter()
    self_pickup = django_filters.BooleanFilter()
    general_delivery = django_filters.BooleanFilter()
    is_on_shop = django_filters.BooleanFilter()
    return_policy = django_filters.BooleanFilter()
    cod = django_filters.BooleanFilter()
    replacement = django_filters.BooleanFilter()
    shop_exchange = django_filters.BooleanFilter()
    shop_warranty = django_filters.BooleanFilter()
    brand_warranty = django_filters.BooleanFilter()
    tax_inclusive = django_filters.BooleanFilter()
    is_popular = django_filters.BooleanFilter()
    is_featured = django_filters.BooleanFilter()
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = product
        exclude = ["image", "gallery_images"]
