from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, mobile, password=None, **extra_fields):
        """Create and return a regular user with a mobile number and password."""
        if not mobile:
            raise ValueError("The Mobile field must be set")
        user = self.model(mobile=mobile, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile, password=None, **extra_fields):
        """Create and return a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(mobile, password, **extra_fields)



from datetime import date
from django.utils import timezone


class OTP(models.Model):
    """Model to store OTP codes for phone number verification"""
    mobile = models.CharField(max_length=15)
    otp_code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['mobile', 'is_verified']),
        ]
    
    def __str__(self):
        return f"OTP for {self.mobile} - {self.otp_code}"
    
    def is_expired(self):
        """Check if OTP has expired"""
        return timezone.now() > self.expires_at


class User(AbstractUser):

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
     


    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, null=True, blank=True)
    address = models.CharField(max_length=225, null=True, blank=True)
    profile_photo = models.ImageField(upload_to="user_image/", blank=True, null=True)
    is_vendor = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)

    mobile = models.CharField(max_length=15, unique=True)
    email = models.EmailField(null=True, blank=True)  # Email is optional

    # Subscription fields (for doctors)
    subscription_valid_from = models.DateField(null=True, blank=True)
    subscription_valid_to = models.DateField(null=True, blank=True)
    subscription_received_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    
    @property
    def subscription_is_active(self):
        """Calculate if subscription is active based on dates"""
        from django.utils import timezone
        today = timezone.now().date()
        if self.subscription_valid_from and self.subscription_valid_to:
            return self.subscription_valid_from <= today <= self.subscription_valid_to
        return False

    username = None  # Remove username field

    USERNAME_FIELD = 'mobile'  # Set mobile as the login field
    REQUIRED_FIELDS = [] 

    objects = CustomUserManager()

    @property
    def age(self):
        if not self.dob:
            return None
        today = date.today()
        return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))

    def __str__(self):
        return self.first_name or self.last_name


class DeviceToken(models.Model):
    """FCM device token for push notifications (one per user)."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="device_token")
    token = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"DeviceToken for {self.user_id}"