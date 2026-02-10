from django.contrib import admin

# Register your models here.

from .models import *


admin.site.register(product)
admin.site.register(vendor_store)
admin.site.register(DeliveryBoy)
admin.site.register(coupon)
admin.site.register(BannerCampaign)
admin.site.register(Offer)
admin.site.register(StoreOffer)
admin.site.register(SpotlightProduct)
admin.site.register(StoreCoverMedia)
admin.site.register(Reel)
admin.site.register(ProductGalleryImage)