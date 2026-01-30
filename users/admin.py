from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, DeviceToken, KYC
from .forms import *  # Import your custom form

class CustomUserAdmin(UserAdmin):
   
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    list_display = ('mobile', 'email', 'is_staff', 'is_active', 'is_customer', 'is_vendor')
    list_filter = ('is_staff', 'is_active', 'is_customer', 'is_vendor')

    fieldsets = (
        (None, {'fields': ('mobile', 'email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser')}),
        ('Roles', {'fields': ('is_customer', 'is_vendor')}),
        ('Groups & Permissions', {'fields': ('groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('mobile', 'email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

    search_fields = ('mobile',)
    ordering = ('mobile',)

admin.site.register(User, CustomUserAdmin)
admin.site.register(DeviceToken)
admin.site.register(KYC)