from django import forms


class LoginForm(forms.Form):
    mobile = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'mobile',
    }))
    password = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password',
        'type': 'password'
    }))


from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User  # Import your User model

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('mobile', 'email')  # Only show mobile + optional email

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('mobile', 'email', 'is_active', 'is_staff', 'is_superuser', 'is_vendor', 'is_subuser', 'is_customer')


from django import forms
from .models import Role, MenuModule, RoleMenuPermission

class RoleWithModulesForm(forms.ModelForm):
    menu_modules = forms.ModelMultipleChoiceField(
        queryset=MenuModule.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Assign Modules"
    )

    class Meta:
        model = Role
        fields = ['name', 'menu_modules']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter role name'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['menu_modules'].initial = MenuModule.objects.filter(
                rolemenupermission__role=self.instance
            )

    def save(self, commit=True):
        role = super().save(commit=False)
        if commit:
            role.save()
            # Clear existing
            RoleMenuPermission.objects.filter(role=role).delete()
            # Add selected
            for module in self.cleaned_data['menu_modules']:
                RoleMenuPermission.objects.create(role=role, menu_module=module)
        return role



class UserRoleAssignForm(forms.ModelForm):
    roles = forms.ModelMultipleChoiceField(
        queryset=Role.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Assign Roles"
    )

    class Meta:
        model = User
        fields = ['mobile', 'email', 'roles']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['roles'].initial = self.instance.roles.all()
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            user.roles.set(self.cleaned_data['roles'])
        return user
    

from .models import *

class UserCreateWithRolesForm(forms.ModelForm):
    
    
    password = forms.CharField(widget=forms.PasswordInput(), label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label="Confirm Password")

    roles = forms.ModelMultipleChoiceField(
        queryset=Role.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Assign Roles"
    )

    class Meta:
        model = User
        fields = ['mobile', 'email', 'password', 'confirm_password', 'is_customer', 'is_vendor']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()

            # Clear old roles if updating
            UserRole.objects.filter(user=user).delete()

            # Assign new roles via UserRole model
            for role in self.cleaned_data.get('roles', []):
                UserRole.objects.create(user=user, role=role)
        return user