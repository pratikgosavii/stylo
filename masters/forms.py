from django import forms

from .models import *
from django.contrib.admin.widgets import  AdminDateWidget, AdminTimeWidget, AdminSplitDateTime


class MainCategoryForm(forms.ModelForm):
    class Meta:
        model = MainCategory
        fields = ['name', 'categories']
        widgets = {
            'categories': forms.CheckboxSelectMultiple(),
        }

class cityForm(forms.ModelForm):
    class Meta:
        model = city
        fields = ['city']
        widgets = {
           
             'city': forms.TextInput(attrs={
                'class': 'form-control', 'id': 'city'
            }),
        }


class StateForm(forms.ModelForm):
    class Meta:
        model = State
        fields = ['name', 'code']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'id': 'name'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'id': 'code'}),
        }

class size_Form(forms.ModelForm):
    class Meta:
        model = size
        fields = ['name', ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 'id': 'name'
            }),
        }


class testimonials_Form(forms.ModelForm):
    class Meta:
        model = testimonials
        fields = '__all__'
        widgets = {
           
            'name': forms.TextInput(attrs={
                'class': 'form-control', 'id': 'name'
            }),

            'rating': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
          
            'description': forms.TextInput(attrs={
                'class': 'form-control', 'id': 'price'
            }),

        }



class expense_category_Form(forms.ModelForm):
    class Meta:
        model = expense_category
        fields = '__all__'
        widgets = {
           
            'name': forms.TextInput(attrs={
                'class': 'form-control', 'id': 'name'
            }),

        }


class product_category_Form(forms.ModelForm):
    class Meta:
        model = product_category
        fields = '__all__'
        widgets = {
           
            'name': forms.TextInput(attrs={
                'class': 'form-control', 'id': 'name'
            }),

            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),


        }

class product_subcategory_Form(forms.ModelForm):
    class Meta:
        model = product_subcategory
        fields = '__all__'
        widgets = {
           
            'category': forms.Select(attrs={
                'class': 'form-control', 'id': 'category'
            }),

            'name': forms.TextInput(attrs={
                'class': 'form-control', 'id': 'name'
            }),

            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),


        }

# class product_Form(forms.ModelForm):
#     class Meta:
#         model = product
#         fields = ['name', 'category', 'description', 'image', 'price', 'rating', 'is_popular', 'is_featured', 'is_active']
#         widgets = {
#             'name': forms.TextInput(attrs={'class': 'form-control'}),
#             'category': forms.Select(attrs={'class': 'form-control'}),
#             'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
#             'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
#             'price': forms.NumberInput(attrs={'class': 'form-control'}),
#             'rating': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0', 'max': '5'}),
#             'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
#         }

class event_Form(forms.ModelForm):
    class Meta:
        model = event
        fields = ['name', 'image', 'description', 'start_date']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control description-box'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),

        }



class customer_address_Form(forms.ModelForm):
    class Meta:
        model = customer_address
        fields = ['name', 'type', 'address', 'landmark', 'pin_code', 'city', 'state']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'landmark': forms.TextInput(attrs={'class': 'form-control'}),
            'pin_code': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
        }


class home_banner_Form(forms.ModelForm):
    class Meta:
        model = home_banner
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'discription': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),

        }