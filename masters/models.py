

from django.db import models


from users.models import User
from django.utils.timezone import now
from datetime import datetime, timezone

import pytz
ist = pytz.timezone('Asia/Kolkata')



from users.models import User





class customer_address(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    address = models.TextField()
    landmark = models.CharField(max_length=255, null=True, blank=True)
    pin_code = models.CharField(max_length=10)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)

    def __str__(self):
        return (
            f"Name: {self.name}, "
            f"Type: {self.type}, "
            f"Address: {self.address}, "
            f"Landmark: {self.landmark or 'N/A'}, "
            f"Pin Code: {self.pin_code}, "
            f"City: {self.city}, "
            f"State: {self.state}"
        )



class testimonials(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class expense_category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class size(models.Model):
    name = models.CharField(max_length=255)


    def __str__(self):
        return self.name

class product_category(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='product_images/')


    def __str__(self):
        return self.name


class MainCategory(models.Model):
    name = models.CharField(max_length=255)
    categories = models.ManyToManyField(product_category, related_name='main_categories')

    def __str__(self):
        return self.name


class product_subcategory(models.Model):
    category = models.ForeignKey("masters.product_category", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='product_images/')


    def __str__(self):
        return self.name



class event(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='doctor_images/')
    start_date = models.DateTimeField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class company(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    brand_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255)
    image = models.ImageField(upload_to='doctor_images/')
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class home_banner(models.Model):
    title = models.CharField(max_length=225, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='homeBanners/')
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    




class city(models.Model):
    city = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.city}"


class State(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.name
