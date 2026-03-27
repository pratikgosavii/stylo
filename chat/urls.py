from django.urls import path
from .views import ChatHistoryAPIView, ChatListAPIView

urlpatterns = [
    path('history/<int:user_id>/', ChatHistoryAPIView.as_view(), name='chat_history'),
    path('list/', ChatListAPIView.as_view(), name='chat_list'),
]
