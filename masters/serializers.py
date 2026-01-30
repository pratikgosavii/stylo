from rest_framework import serializers
from .models import *




class customer_address_serializer(serializers.ModelSerializer):
    
    class Meta:
        model = customer_address
        fields = '__all__'
        read_only_fields = ['user']

    def create(self, validated_data):
        # Inject authenticated user manually
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    

    
class testimonials_serializer(serializers.ModelSerializer):
    class Meta:
        model = testimonials
        fields = '__all__'



    
class city_serializer(serializers.ModelSerializer):
    class Meta:
        model = city
        fields = '__all__'


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = '__all__'




class product_category_serializer(serializers.ModelSerializer):
    class Meta:
        model = product_category
        fields = '__all__'



class size_serializer(serializers.ModelSerializer):
    class Meta:
        model = size
        fields = '__all__'



class product_main_category_serializer(serializers.ModelSerializer):
    category_details = product_category_serializer(source='categories', many=True, read_only=True)

    class Meta:
        model = MainCategory
        fields = ['id', 'name', 'category_details']



class product_subcategory_serializer(serializers.ModelSerializer):
    class Meta:
        model = product_subcategory
        fields = '__all__'


class expense_category_serializer(serializers.ModelSerializer):
    class Meta:
        model = expense_category
        fields = '__all__'

















class event_serializer(serializers.ModelSerializer):
    class Meta:
        model = event
        fields = '__all__'



# Step 1: Create a serializer
class HomeBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = home_banner
        fields = ['image'] 
    
    def get_image(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = company
        fields = '__all__'
        read_only_fields = ['user']


    