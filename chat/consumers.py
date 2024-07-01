import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from chat.models import Applicant, Conversation, Message
import logging

from notification.models import Notification

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    online_users = {}

    async def connect(self):
        print(333)
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.conversation_group_name = f'chat_{self.conversation_id}'

        # 如果聊天室还没有在线用户，则初始化计数器
        if self.conversation_group_name not in ChatConsumer.online_users:
            ChatConsumer.online_users[self.conversation_group_name] = 0

        # 用户加入聊天室，在线用户数量加1
        ChatConsumer.online_users[self.conversation_group_name] += 1

        print("进入聊天室")

        # Join conversation group
        await self.channel_layer.group_add(
            self.conversation_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # 用户离开聊天室，在线用户数量减1
        ChatConsumer.online_users[self.conversation_group_name] -= 1

        # Leave conversation group
        await self.channel_layer.group_discard(
            self.conversation_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json.get('action')

        if action == 'send_message':
            user_id = text_data_json['userId']
            content = text_data_json['content']
            await self.handle_send_message(user_id, content)
        elif action == 'read_message':
            # if ChatConsumer.online_users[self.conversation_group_name] > 1:
            user_id = text_data_json['userId']
            await self.handle_read_message(user_id)

    async def handle_send_message(self, user_id, content):
        sender = await self.get_applicant(user_id)
        conversation = await self.get_conversation(self.conversation_id)
        message = await self.create_message(sender, conversation, content)
        await self.message_notification(sender, content)

        await self.channel_layer.group_send(
            self.conversation_group_name,
            {
                'type': 'chat_message',
                'message': message.content,
                'timestamp': str(message.timestamp),
                'sender': sender.id,
                'message_id': message.id,
            }
        )

    async def handle_read_message(self, user_id):
        await self.mark_messages_as_read(user_id, self.conversation_id)

        if ChatConsumer.online_users[self.conversation_group_name] > 1:
            await self.channel_layer.group_send(
                self.conversation_group_name,
                {
                    'type': 'messages_read',
                    'user_id': user_id,
                }
            )
        else:
            await self.channel_layer.group_send(
                self.conversation_group_name,
                {
                    'type': 'messages_read_single',
                    'user_id': user_id,
                }
            )

    async def chat_message(self, event):
        message = event['message']
        timestamp = event['timestamp']
        sender = event['sender']
        message_id = event['message_id']

        await self.send(text_data=json.dumps({
            'action': 'chat_message',
            'message': message,
            'timestamp': timestamp,
            'sender': sender,
            'message_id': message_id,
        }))
        # 检查当前聊天室是否有多个在线用户
        # if ChatConsumer.online_users[self.conversation_group_name] > 1:
        await self.handle_read_message(sender)

    async def messages_read(self, event):
        user_id = event['user_id']

        await self.send(text_data=json.dumps({
            'action': 'messages_read',
            'user_id': user_id,
        }))

    async def messages_read_single(self, event):
        user_id = event['user_id']

        await self.send(text_data=json.dumps({
            'action': 'messages_read_single',
            'user_id': user_id,
        }))

    @database_sync_to_async
    def get_applicant(self, user_id):
        return Applicant.objects.get(id=user_id)

    @database_sync_to_async
    def get_conversation(self, conversation_id):
        return Conversation.objects.get(id=conversation_id)

    @database_sync_to_async
    def create_message(self, sender, conversation, content):
        message = Message.objects.create(sender=sender, conversation=conversation, content=content)
        conversation.last_message = message.timestamp
        conversation.save()
        return message

    @database_sync_to_async
    def mark_messages_as_read(self, user_id, conversation_id):
        messages = Message.objects.filter(conversation_id=conversation_id).exclude(sender_id=user_id)
        for message in messages:
            message.is_read = True
            message.save()

    @database_sync_to_async
    def message_notification(self, sender, content):
        print("handle notification")
        conversations = Conversation.objects.get(id=self.conversation_id)
        user = list(conversations.participants.exclude(id=sender.id).values())
        try:
            # 构建消息实体
            notification = Notification()
            notification.user_id = user[0]["id"]
            notification.title = f"{sender.user_name}发来一个消息"
            notification.type = 7
            notification.message = content
            notification.is_read = 0
            notification.related_user_id = sender.id
            notification.save()
            print("finish")
        except Exception as e:
            print(f"Error sending message: {e}")