from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ChatMessage

User = get_user_model()

class UserBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'mobile', 'profile_photo']

class ChatMessageSerializer(serializers.ModelSerializer):
    sender = UserBriefSerializer(read_only=True)
    receiver = UserBriefSerializer(read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'sender', 'receiver', 'message', 'is_seen', 'is_delivered', 'timestamp']
