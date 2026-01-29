

from django.db import models


from users.models import User
from django.utils.timezone import now
from datetime import datetime, timezone

import pytz
ist = pytz.timezone('Asia/Kolkata')



from users.models import User




class coupon(models.Model):

    COUPON_TYPE_CHOICES = [
    ("discount", "Discount Coupon"),
    ("no_return", "No Return & Exchange"),
    ("online_pay", "Online Pay"),
    ]

    TYPE_CHOICES = [
        ('percent', 'Percentage'),
        ('amount', 'Amount'),
    ]
    
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, null=True, blank=True)
    coupon_type = models.CharField(max_length=10, choices=COUPON_TYPE_CHOICES, default='percent')  # 👈 Add this
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='percent')  # 👈 Add this
    customer_id = models.IntegerField(null=True, blank=True)
    code = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=500, null=True, blank=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='doctor_images/', null=True, blank=True)
    start_date = models.DateTimeField(default=now)
    end_date = models.DateTimeField()
    only_followers = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code


class vendor_store(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="vendor_store", blank=True, null=True)
    name = models.CharField(max_length=50)
    storetag = models.CharField(max_length=50, blank=True, null=True)
    banner_image = models.ImageField(upload_to='store/', blank=True, null=True)
    profile_image = models.ImageField(upload_to='store/', blank=True, null=True)
    about = models.CharField(max_length=500, blank=True, null=True)
    latitude = models.DecimalField(max_digits=50, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=50, decimal_places=6, blank=True, null=True)
    is_location = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_online = models.BooleanField(default=False)
    is_offline = models.BooleanField(default=False)
    display_as_catalog = models.BooleanField(default=False)
    private_catalog = models.BooleanField(default=False)
    

class Reel(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # user who created post
    media = models.FileField(upload_to='posts/')  # upload media
    description = models.TextField(blank=True)
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, blank=True)
    boost_post = models.BooleanField(default=False)
    budget = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)



class BannerCampaign(models.Model):
  
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name='banners')
    banner_image = models.ImageField(upload_to='campaign_banners/', help_text="Max 1MB, Ratio 1:3")
    campaign_name = models.CharField(max_length=255)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.campaign_name
    



class product(models.Model):

    SIZE_CHOICES = (
        ('XL', 'XL'),
        ('M', 'M'),
        ('L', 'L'),
        ('S', 'S'),
        ('XS', 'XS'),
        ('2XL', '2XL'),
    )


    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name='productssdsdsd', null=True, blank=True)

    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="variants")
    
    name = models.CharField(max_length=255)
    category = models.ForeignKey("masters.product_category", on_delete=models.CASCADE)
    sub_category = models.ForeignKey("masters.product_subcategory", related_name='sdfdsz', on_delete=models.CASCADE)

    # Pricing details
    wholesale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sales_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    mrp = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
   
    hsn = models.CharField(max_length=50, null=True, blank=True)
    gst = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    sgst_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    cgst_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # Stock
    erial_numbers = models.DecimalField(max_digits=30, decimal_places=0)
    opening_stock = models.IntegerField(null=True, blank=True)
    stock = models.IntegerField(null=True, blank=True)

    # Optional
    brand_name = models.CharField(max_length=255, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    size = models.ForeignKey("masters.size", on_delete=models.CASCADE, null=True, blank=True)
    batch_number = models.CharField(max_length=100, null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)

    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    gallery_images = models.ImageField(upload_to='product_gallery/', null=True, blank=True)

    replacement = models.BooleanField(default=False)
    shop_exchange = models.BooleanField(default=False)
    shop_warranty = models.BooleanField(default=False)
    brand_warranty = models.BooleanField(default=False)

    # Flags
    tax_inclusive = models.BooleanField(default=False)
    is_popular = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    stock_cached = models.IntegerField(default=0, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.gst is not None:
            half_gst = round(self.gst / 2, 2)
            self.sgst_rate = half_gst
            self.cgst_rate = half_gst
        super().save(*args, **kwargs)


    @property
    def current_stock(self):
        if self.track_serial_numbers:
            return self.serials.filter(is_sold=False).count()
        return self.stock or 0




class DeliveryBoy(models.Model):
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    photo = models.ImageField(upload_to='delivery_boys/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    total_deliveries = models.PositiveIntegerField(default=0)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    account_user = models.OneToOneField("users.User", on_delete=models.CASCADE, related_name="delivery_boy_profile", null=True, blank=True)

    
class Offer(models.Model):
   

    request = models.ForeignKey(
        'customer.ProductRequest',
        on_delete=models.CASCADE,
        related_name="offers"
    )
    seller = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name="offers"
    )
    product = models.CharField(max_length=50, blank=True, null=True)
    heading = models.CharField(max_length=255)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    media = models.ImageField(upload_to="offers/media/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    valid_till = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Offer automatically expires after 7 days
        if not self.valid_till:
            from datetime import timedelta, datetime
            self.valid_till = datetime.now() + timedelta(days=7)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.heading} - {self.seller.username}"

