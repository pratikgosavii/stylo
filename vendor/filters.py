import django_filters
from .models import *
from django.db.models import Q

class productFilter(django_filters.FilterSet):

    search = django_filters.CharFilter(method='filter_by_search', label='Search')
    sale_type = django_filters.CharFilter(method='filter_by_sale_type', label='Sale Type')

    class Meta:
        model = product
        exclude = ['image', 'gallery_images', 'size_chart_image', 'user']

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
    """
    All filters for ListProducts API.
    Query params: ?name=...&category=...&min_price=...&store_id=... etc.
    """
    # Search (name, brand_name, description)
    search = django_filters.CharFilter(method="filter_search", label="Search")

    # Text fields (partial match)
    name = django_filters.CharFilter(lookup_expr="icontains")
    brand_name = django_filters.CharFilter(lookup_expr="icontains")
    description = django_filters.CharFilter(lookup_expr="icontains")
    batch_number = django_filters.CharFilter(lookup_expr="icontains")
    hsn = django_filters.CharFilter(lookup_expr="icontains")

    # Price ranges (sales_price)
    min_price = django_filters.NumberFilter(field_name="sales_price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="sales_price", lookup_expr="lte")

    # MRP ranges
    min_mrp = django_filters.NumberFilter(field_name="mrp", lookup_expr="gte")
    max_mrp = django_filters.NumberFilter(field_name="mrp", lookup_expr="lte")

    # Stock range
    min_stock = django_filters.NumberFilter(field_name="stock", lookup_expr="gte")
    max_stock = django_filters.NumberFilter(field_name="stock", lookup_expr="lte")
    in_stock = django_filters.BooleanFilter(method="filter_in_stock", label="In stock")

    # Expiry date ranges
    expiry_before = django_filters.DateFilter(field_name="expiry_date", lookup_expr="lte")
    expiry_after = django_filters.DateFilter(field_name="expiry_date", lookup_expr="gte")

    # Category / store filters
    main_category_id = django_filters.NumberFilter(field_name="category__main_category_id")
    category_id = django_filters.NumberFilter(field_name="category_id")
    sub_category_id = django_filters.NumberFilter(field_name="sub_category_id")
    store_id = django_filters.NumberFilter(method="filter_store_id", label="Store ID (products from this store)")
    user_id = django_filters.NumberFilter(field_name="user_id")

    # Foreign keys
    category = django_filters.ModelChoiceFilter(queryset=product_category.objects.all())
    sub_category = django_filters.ModelChoiceFilter(queryset=product_subcategory.objects.all())
    size_id = django_filters.NumberFilter(field_name="size_id")
    color_id = django_filters.NumberFilter(field_name="color_id")

    # Choice fields
    fabric_type = django_filters.ChoiceFilter(choices=product.FABRIC_TYPE_CHOICES)

    # Boolean fields
    tax_inclusive = django_filters.BooleanFilter()
    is_popular = django_filters.BooleanFilter()
    is_featured = django_filters.BooleanFilter()
    is_active = django_filters.BooleanFilter()

    def filter_search(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(name__icontains=value)
                | Q(brand_name__icontains=value)
                | Q(description__icontains=value)
            )
        return queryset

    def filter_store_id(self, queryset, name, value):
        """Filter products by store: store has user, products have user (vendor)."""
        if value is not None:
            from vendor.models import vendor_store
            try:
                store = vendor_store.objects.get(id=value)
                if store.user_id:
                    return queryset.filter(user_id=store.user_id)
            except vendor_store.DoesNotExist:
                pass
        return queryset

    def filter_in_stock(self, queryset, name, value):
        if value is True:
            return queryset.filter(Q(stock__gt=0) | Q(stock__isnull=True))
        if value is False:
            return queryset.filter(stock=0)
        return queryset

    class Meta:
        model = product
        exclude = ["image", "gallery_images", "size_chart_image"]
