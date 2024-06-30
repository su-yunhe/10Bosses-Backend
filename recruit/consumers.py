import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print('connected')
        await self.channel_layer.group_add(
            'recruitment_update',
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            'recruitment_update',
            self.channel_name
        )

    async def receive(self, text_data):
        pass

    async def update_message(self, event):
        print(event['message'])
        await self.send(text_data=json.dumps({
            'message': event['message']
        }))
