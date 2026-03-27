import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatMessage

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        if self.user.is_anonymous:
            await self.close()
            return
            
        self.room_group_name = f"user_{self.user.id}"
        
        # Join personal room
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            # Leave personal room
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action', 'chat_message')
        
        if action == 'chat_message':
            receiver_id = data.get('receiver_id')
            message = data.get('message')
            
            if receiver_id and message:
                msg_obj = await self.save_message(self.user.id, receiver_id, message)
                
                # Send to receiver's group
                receiver_group = f"user_{receiver_id}"
                await self.channel_layer.group_send(
                    receiver_group,
                    {
                        "type": "chat_message",
                        "id": msg_obj.id,
                        "sender_id": self.user.id,
                        "receiver_id": receiver_id,
                        "message": message,
                        "timestamp": str(msg_obj.timestamp),
                        "is_seen": False,
                        "is_delivered": False,
                    }
                )
                
                # Echo back to sender for confirmation
                await self.send(text_data=json.dumps({
                    "action": "message_sent",
                    "id": msg_obj.id,
                    "receiver_id": receiver_id,
                    "message": message,
                    "timestamp": str(msg_obj.timestamp)
                }))

        elif action == 'message_delivered':
            message_id = data.get('message_id')
            sender_id = data.get('sender_id')
            
            if message_id and sender_id:
                await self.mark_delivered(message_id)
                # Notify sender
                await self.channel_layer.group_send(
                    f"user_{sender_id}",
                    {
                        "type": "status_update",
                        "message_id": message_id,
                        "status": "delivered"
                    }
                )
                
        elif action == 'message_seen':
            message_id = data.get('message_id')
            sender_id = data.get('sender_id')
            
            if message_id and sender_id:
                await self.mark_seen(message_id)
                # Notify sender
                await self.channel_layer.group_send(
                    f"user_{sender_id}",
                    {
                        "type": "status_update",
                        "message_id": message_id,
                        "status": "seen"
                    }
                )

    async def chat_message(self, event):
        # Prevent receiving if disconnected
        await self.send(text_data=json.dumps({
            "action": "chat_message",
            "id": event["id"],
            "sender_id": event["sender_id"],
            "receiver_id": event["receiver_id"],
            "message": event["message"],
            "timestamp": event["timestamp"],
            "is_seen": event["is_seen"],
            "is_delivered": event["is_delivered"]
        }))

    async def status_update(self, event):
        await self.send(text_data=json.dumps({
            "action": "status_update",
            "message_id": event["message_id"],
            "status": event["status"]
        }))

    @database_sync_to_async
    def save_message(self, sender_id, receiver_id, message):
        return ChatMessage.objects.create(
            sender_id=sender_id,
            receiver_id=receiver_id,
            message=message
        )

    @database_sync_to_async
    def mark_delivered(self, message_id):
        ChatMessage.objects.filter(id=message_id).update(is_delivered=True)

    @database_sync_to_async
    def mark_seen(self, message_id):
        ChatMessage.objects.filter(id=message_id).update(is_seen=True, is_delivered=True)
