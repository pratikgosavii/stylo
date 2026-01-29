import django_filters
from .models import *

class EventFilter(django_filters.FilterSet):
    class Meta:
        model = event
        exclude = ['image']  # ⛔ Exclude unsupported field

class product_categoryFilter(django_filters.FilterSet):
    class Meta:
        model = product_category
        exclude = ['image']  # ⛔ Exclude unsupported field
