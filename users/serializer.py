
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import *
# from masters.models import *
# from masters.serializers import *


# from customer.models import *


from rest_framework import serializers

class UserProfileSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'id',
            'mobile',
            'profile_photo',
            'first_name',
            'last_name',
            'email',
            'dob',
            'gender',
            'address',
            'is_vendor',
            'is_customer',
            'password',  # Include this for input only
        ]
        read_only_fields = ['id', 'mobile']
        extra_kwargs = {
            'email': {'required': False, 'allow_blank': True, 'allow_null': True},
        }

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


    



# class User_KYCSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = user_kyc
#         fields = ['id', 'user', 'adhar_card', 'pan_card', 'driving_licence', 'approved']
#         read_only_fields = ['user', 'approved']



# serializers.py

# from rest_framework import serializers
# from .models import Notification

# class NotificationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Notification
#         fields = ['id', 'title', 'message', 'is_read', 'created_at']
