from django.utils import timezone

from django.db import models

# Create your models here.


import random



from users.models import User

from django.db import models

class Address(models.Model):
    STATE_CHOICES = [
        ("Andhra Pradesh", "Andhra Pradesh"),
        ("Arunachal Pradesh", "Arunachal Pradesh"),
        ("Assam", "Assam"),
        ("Bihar", "Bihar"),
        ("Chhattisgarh", "Chhattisgarh"),
        ("Goa", "Goa"),
        ("Gujarat", "Gujarat"),
        ("Haryana", "Haryana"),
        ("Himachal Pradesh", "Himachal Pradesh"),
        ("Jharkhand", "Jharkhand"),
        ("Karnataka", "Karnataka"),
        ("Kerala", "Kerala"),
        ("Madhya Pradesh", "Madhya Pradesh"),
        ("Maharashtra", "Maharashtra"),
        ("Manipur", "Manipur"),
        ("Meghalaya", "Meghalaya"),
        ("Mizoram", "Mizoram"),
        ("Nagaland", "Nagaland"),
        ("Odisha", "Odisha"),
        ("Punjab", "Punjab"),
        ("Rajasthan", "Rajasthan"),
        ("Sikkim", "Sikkim"),
        ("Tamil Nadu", "Tamil Nadu"),
        ("Telangana", "Telangana"),
        ("Tripura", "Tripura"),
        ("Uttar Pradesh", "Uttar Pradesh"),
        ("Uttarakhand", "Uttarakhand"),
        ("West Bengal", "West Bengal"),
        ("Andaman and Nicobar Islands", "Andaman and Nicobar Islands"),
        ("Chandigarh", "Chandigarh"),
        ("Dadra and Nagar Haveli and Daman and Diu", "Dadra and Nagar Haveli and Daman and Diu"),
        ("Delhi", "Delhi"),
        ("Jammu and Kashmir", "Jammu and Kashmir"),
        ("Ladakh", "Ladakh"),
        ("Lakshadweep", "Lakshadweep"),
        ("Puducherry", "Puducherry"),
    ]

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="addresses")
    
    full_name = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=15)
    city = models.CharField(max_length=60)
    flat_building = models.CharField(max_length=255)
    area_street = models.CharField(max_length=255)
    landmark = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=100, choices=STATE_CHOICES)  # 🔽 dropdown
    latitude = models.DecimalField(max_digits=50, decimal_places=6)
    longitude = models.DecimalField(max_digits=50, decimal_places=6)

    is_default = models.BooleanField(default=False)
    delivery_instructions = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        parts = [self.full_name] if self.full_name else []
        if self.city:
            parts.append(self.city)
        if self.state:
            parts.append(self.state)
        return " - ".join(str(p) for p in parts) if parts else "Address"
    
    @property
    def full_address(self):
        parts = [
            self.flat_building,
            self.area_street,
            self.landmark if self.landmark else "",
            f"{self.city}, {self.state}"
        ]
        return ", ".join([p for p in parts if p])  # removes blanks

    @property
    def full_address(self):
        parts = [
            self.flat_building,
            self.area_street,
            self.landmark if self.landmark else "",
            f"{self.city}, {self.state}"
        ]
        return ", ".join([p for p in parts if p])  # removes blanks

    
class Cart(models.Model):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="carts"
    )
    product = models.ForeignKey(
        "vendor.product",  # or Product model
        on_delete=models.CASCADE,
        related_name="carts"
    )
    quantity = models.PositiveIntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'product')  # one product per user cart

    def __str__(self):
        return f"{self.user.username} - {self.product.name} x {self.quantity}"
    


class Order(models.Model):

    user = models.ForeignKey(
            "users.User",
            on_delete=models.CASCADE,
            related_name="orders", blank=True, null=True
    )

    ORDER_STATUS = [
        ('ready_to_dispatch', 'Ready to Dispatch'),
        ('not_accepted', 'Not Accepted'),
        ('accepted', 'Accepted'),
        ('in_transit', 'In Transit'),
        ('trial_begin', 'Trial Begin'),
        ('trial_ended', 'Trial Ended'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    DELIVERY_TYPES = [
        ('instant_delivery', 'Instant Delivery'),
        ('general_delivery', 'General Delivery'),
        ('self_pickup', 'Self Pickup'),
        ('on_shop_order', 'On-shop Order'),
    ]

    order_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='not_accepted')  # ready_to_dispatch, not_accepted, accepted, in_transit, trial_begin, trial_ended, cancelled, completed
    payment_mode = models.CharField(max_length=50, default='COD')
    is_paid = models.BooleanField(default=False)

    # Cashfree / payment gateway fields
    payment_gateway = models.CharField(max_length=20, blank=True, null=True, help_text="cod, cashfree, razorpay")
    pg_order_id = models.CharField(max_length=100, blank=True, null=True, help_text="Cashfree cf_order_id / Razorpay order id")
    payment_id = models.CharField(max_length=100, blank=True, null=True, help_text="Cashfree cf_payment_id / transaction id")
    payment_status = models.CharField(max_length=30, blank=True, null=True, help_text="pending, success, failed, refunded")
    payment_method = models.CharField(max_length=50, blank=True, null=True, help_text="upi, card, netbanking, wallet")
      
    # Delivery verification OTP
    delivery_otp = models.CharField(max_length=6, blank=True, null=True)
    delivery_otp_generated_at = models.DateTimeField(blank=True, null=True)

    # Trial OTP (6-digit, generated when order is created; customer enters OTP to mark trial_begin)
    trial_otp = models.CharField(max_length=6, blank=True, null=True)
    trial_begins_at = models.DateTimeField(blank=True, null=True, help_text="Set when customer verifies trial OTP (trial begin)")
    trial_ends_at = models.DateTimeField(blank=True, null=True, help_text="Set when customer ends trial (trial ended)")

    delivery_type = models.CharField(
        max_length=50,
        choices=DELIVERY_TYPES,
        default='self_pickup'
    )

    # Financials
    item_total = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    wallet_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cashback = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coupon = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Delivery details
    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True, blank=True)
    instruction = models.TextField(blank=True, null=True)
    
    delivery_boy = models.ForeignKey("vendor.DeliveryBoy", null=True, blank=True, on_delete=models.SET_NULL, related_name="assigned_orders")
    created_at = models.DateTimeField(auto_now=True)

    # Cancellation reasons (when customer cancels after trial)
    cancel_size_doesnt_fit = models.BooleanField(default=False)
    cancel_color_looks_different = models.BooleanField(default=False)
    cancel_material_quality_not_expected = models.BooleanField(default=False)
    cancel_style_doesnt_suit = models.BooleanField(default=False)
    cancel_other = models.BooleanField(default=False)
    cancel_other_reason = models.TextField(blank=True, null=True, help_text="Text reason when 'other' is selected")

    
    

class OrderItem(models.Model):
    """Item-level statuses only: trial, ordered, cancelled. Accepted/rejected/in_transit/delivered live on Order only."""
    STATUS_CHOICES = [
        ('trial', 'Trial'),
        ('ordered', 'Ordered'),
        ('cancelled', 'Cancelled'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("vendor.product", on_delete=models.CASCADE, related_name="items")
    quantity = models.IntegerField(default=1)
    price = models.IntegerField()
    status = models.CharField(max_length=28, choices=STATUS_CHOICES, default='trial')
    tracking_link = models.URLField(max_length=500, blank=True, null=True)

    def total_price(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.product} × {self.quantity} ({self.status})"




from vendor.models import product


class Follower(models.Model):
    """Track user follow relationships: follower follows user"""
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name='followers')
    follower = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name='following')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'follower')
        
    def __str__(self):
        return f"{self.follower.username} follows {self.user.username}"


class Favourite(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="favourites")
    product = models.ForeignKey(product, on_delete=models.CASCADE, related_name="favourited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")

class FavouriteStore(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="favourites_user")
    store = models.ForeignKey("vendor.vendor_store", on_delete=models.CASCADE, related_name="favourited_store")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "store")


class ReelLike(models.Model):
    """Customer like on a reel. One like per user per reel."""
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="reel_likes")
    reel = models.ForeignKey("vendor.Reel", on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "reel")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} likes reel {self.reel_id}"


class ReelComment(models.Model):
    """Customer comment on a reel."""
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="reel_comments")
    reel = models.ForeignKey("vendor.Reel", on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.user} on reel {self.reel_id}"



        
class SupportTicket(models.Model):
    ROLE_CHOICES = [
        ("vendor", "Vendor"),
        ("customer", "Customer"),
        ("admin", "Admin"),
    ]
   
    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    ]

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="support_tickets")
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)  # who created ticket
    subject = models.CharField(max_length=255)
    order = models.ForeignKey(
        "customer.Order",   # replace with your actual Appointment model
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="support_tickets"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ticket #{self.id} - {self.subject}"



class TicketMessage(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name="messages", blank=True, null=True)
    sender = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="sent_support_messages")
    message = models.TextField()
    is_admin = models.BooleanField(default=False)
    attachment = models.FileField(upload_to="support/attachments/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Msg by {self.sender.username} in Ticket {self.ticket.id}"







class Review(models.Model):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='product_reviews')
    user = models.ForeignKey("users.user", on_delete=models.CASCADE, related_name='reviews', blank=True, null=True)
    rating = models.PositiveSmallIntegerField()  # 1 to 5 stars
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    photo = models.ImageField(upload_to="review/photos/", blank=True, null=True)  # legacy single photo
    is_visible = models.BooleanField(default=False)

    class Meta:
        unique_together = ('order_item', 'user')  # ensures 1 review per user per product
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user}"


class ReviewPhoto(models.Model):
    """Multiple photos per review."""
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to="review/photos/")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']



        
class ProductRequest(models.Model):
    TYPE_CHOICES = [
        ('personal', 'Personal use'),
        ('business', 'For Business'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="requests")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    product_name = models.CharField(max_length=255)
    category = models.ForeignKey("masters.product_category", on_delete=models.CASCADE)
    sub_category = models.ForeignKey("masters.product_subcategory", related_name='sdfsdsa', on_delete=models.CASCADE)
    budget = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to="requests/photos/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product_name} ({self.user.username})"