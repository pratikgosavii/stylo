from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ChatMessage
from django.contrib.auth import get_user_model
from django.db.models import Q
from .serializers import ChatMessageSerializer, UserBriefSerializer

User = get_user_model()

class ChatHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        # We also need to mark messages as seen if fetched by the receiver
        messages = ChatMessage.objects.filter(
            Q(sender=request.user, receiver_id=user_id) | 
            Q(sender_id=user_id, receiver=request.user)
        ).order_by('timestamp')
        
        # Mark unread messages from this user as seen
        unread = messages.filter(receiver=request.user, is_seen=False)
        unread.update(is_seen=True, is_delivered=True)
        
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)


class ChatListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Fetch all messages involving the current user
        messages = ChatMessage.objects.filter(
            Q(sender=request.user) | Q(receiver=request.user)
        ).order_by('-timestamp')
        
        # We need distinctive users and the latest message with them
        chat_partners = {}
        
        for msg in messages:
            # Figure out who the OTHER person is
            other_user = msg.receiver if msg.sender == request.user else msg.sender
            
            if other_user.id not in chat_partners:
                chat_partners[other_user.id] = {
                    'user': UserBriefSerializer(other_user).data,
                    'latest_message': ChatMessageSerializer(msg).data,
                    'unread_count': 0
                }
            
            # If I am the receiver and it's not seen, increment unread count
            if msg.receiver == request.user and not msg.is_seen:
                chat_partners[other_user.id]['unread_count'] += 1
                
        # Convert dict to list
        results = list(chat_partners.values())
        return Response(results)
