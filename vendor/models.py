

from django.db import models


from users.models import User
from django.utils.timezone import now
from datetime import datetime, timezone

import pytz
ist = pytz.timezone('Asia/Kolkata')




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
    """Store Creation: store name, business type, description, logo, cover; Registered Business Address; optional vendor/owner address and contact."""

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="vendor_store", blank=True, null=True)
    name = models.CharField(max_length=255, help_text="Store name")
    storetag = models.CharField(max_length=50, blank=True, null=True)
    banner_image = models.ImageField(upload_to='store/', blank=True, null=True)
    profile_image = models.ImageField(upload_to='store/', blank=True, null=True, help_text="Store logo")
    about = models.CharField(max_length=500, blank=True, null=True, help_text="Store description")
    business_type = models.CharField(max_length=100, blank=True, null=True, help_text="Business type")

    # Store contact
    store_mobile = models.CharField(max_length=20, blank=True, null=True)
    store_email = models.EmailField(blank=True, null=True)

    # Registered Business Address (Store address)
    house_building_no = models.CharField(max_length=255, blank=True, null=True, help_text="House/Building/Apartment No.")
    locality_street = models.CharField(max_length=255, blank=True, null=True, help_text="Locality/Area/Street")
    pincode = models.CharField(max_length=20, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)

    # Vendor/Owner (optional – vendor name comes from user; address if different from store)
    owner_gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    vendor_house_no = models.CharField(max_length=255, blank=True, null=True)
    vendor_locality_street = models.CharField(max_length=255, blank=True, null=True)
    vendor_pincode = models.CharField(max_length=20, blank=True, null=True)
    vendor_state = models.CharField(max_length=100, blank=True, null=True)
    vendor_city = models.CharField(max_length=100, blank=True, null=True)

    latitude = models.DecimalField(max_digits=50, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=50, decimal_places=6, blank=True, null=True)
    is_location = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_online = models.BooleanField(default=False)


class StoreCoverMedia(models.Model):
    """Store cover photos or videos (multiple). Each item is either image or video."""
    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    store = models.ForeignKey(
        vendor_store,
        on_delete=models.CASCADE,
        related_name="cover_media",
    )
    media_type = models.CharField(
        max_length=10,
        choices=MEDIA_TYPE_CHOICES,
        default='image',
        help_text="Photo or video",
    )
    media = models.FileField(upload_to="store/cover_media/", help_text="Cover photo or video file")
    order = models.PositiveIntegerField(default=0, help_text="Display order (lower first)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"Cover media #{self.order} for {self.store.name}"


class Reel(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # user who created post
    media = models.FileField(upload_to='posts/')  # upload media
    description = models.TextField(blank=True)
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)



class BannerCampaign(models.Model):
  
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name='banners')
    main_category = models.ForeignKey("masters.MainCategory", on_delete=models.SET_NULL, null=True, blank=True, related_name='banner_campaigns')
    store = models.ForeignKey(vendor_store, on_delete=models.CASCADE, null=True, blank=True, related_name='banners')
    product = models.ForeignKey("product", on_delete=models.SET_NULL, null=True, blank=True, related_name='banner_campaigns')
    banner_image = models.ImageField(upload_to='campaign_banners/', help_text="Max 1MB, Ratio 1:3")
    campaign_name = models.CharField(max_length=255)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.campaign_name
    



class ProductGalleryImage(models.Model):
    """Multiple gallery images per product."""
    product = models.ForeignKey("product", on_delete=models.CASCADE, related_name="gallery_images")
    image = models.ImageField(upload_to='product_gallery/')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"Gallery #{self.order} for product {self.product_id}"


class product(models.Model):

    SIZE_CHOICES = (
        ('XL', 'XL'),
        ('M', 'M'),
        ('L', 'L'),
        ('S', 'S'),
        ('XS', 'XS'),
        ('2XL', '2XL'),
    )

    FABRIC_TYPE_CHOICES = [
        ('cotton', 'Cotton'),
        ('polyester', 'Polyester'),
        ('silk', 'Silk'),
        ('wool', 'Wool'),
        ('linen', 'Linen'),
        ('rayon', 'Rayon'),
        ('nylon', 'Nylon'),
        ('denim', 'Denim'),
        ('velvet', 'Velvet'),
        ('chiffon', 'Chiffon'),
        ('georgette', 'Georgette'),
        ('satin', 'Satin'),
        ('leather', 'Leather'),
        ('blend', 'Blend'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name='productssdsdsd', null=True, blank=True)

    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="variants")
    
    name = models.CharField(max_length=255)
    main_category = models.ForeignKey("masters.MainCategory", on_delete=models.CASCADE, null=True, blank=True, related_name="products")
    category = models.ForeignKey("masters.product_category", on_delete=models.CASCADE)
    sub_category = models.ForeignKey("masters.product_subcategory", related_name='sdfdsz', on_delete=models.CASCADE)

    # Pricing details
    sales_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    mrp = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
   
    gst = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # Stock
    serial_numbers = models.CharField(max_length=100, blank=True, null=True)
    opening_stock = models.IntegerField(null=True, blank=True)
    stock = models.IntegerField(null=True, blank=True)

    # Optional
    brand_name = models.CharField(max_length=255, null=True, blank=True)
    color = models.ForeignKey("masters.color", on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    fabric_type = models.CharField(max_length=20, choices=FABRIC_TYPE_CHOICES, null=True, blank=True)
    size = models.ForeignKey("masters.size", on_delete=models.CASCADE, null=True, blank=True)
    size_chart_image = models.ImageField(upload_to='product_size_charts/', null=True, blank=True)
    batch_number = models.CharField(max_length=100, null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)

    description = models.TextField(null=True, blank=True)

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
        super().save(*args, **kwargs)


    @property
    def current_stock(self):
        if self.track_serial_numbers:
            return self.serials.filter(is_sold=False).count()
        return self.stock or 0


class SpotlightProduct(models.Model):
    """Vendor spotlight: product + optional discount tag for display."""
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, null=True, blank=True, related_name="spotlight_products")
    product = models.ForeignKey("product", on_delete=models.CASCADE, related_name="spotlight_entries")
    discount_tag = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.product.name


class DeliveryBoy(models.Model):
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=150, unique=True, blank=True, null=True, help_text="Login username for delivery boy")
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


class StoreOffer(models.Model):
    """Promotional offer: title, description, image, valid from/to."""

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="store_offers",
    )
    offer_title = models.CharField(max_length=255)
    offer_description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="store_offers/", blank=True, null=True)
    valid_from = models.DateField(blank=True, null=True)
    valid_to = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.offer_title

