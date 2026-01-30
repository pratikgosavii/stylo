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
        fields = ('mobile', 'email', 'is_active', 'is_staff', 'is_superuser', 'is_vendor', 'is_customer')


class UserCreateWithRolesForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label="Confirm Password")

    class Meta:
        model = User
        fields = ['mobile', 'email', 'password', 'confirm_password', 'is_customer', 'is_vendor']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
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
        return user