from django.contrib import admin
from .models import *

# Register your models here.

from .models import *

admin.site.register(customer_address)
admin.site.register(testimonials)
admin.site.register(MainCategory)
admin.site.register(product_category)
admin.site.register(product_subcategory)
