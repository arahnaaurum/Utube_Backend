import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # my_id = self.scope['user'].id
        # other_user_id = self.scope['url_route']['kwargs']['id']
        # print(my_id)
        ids = (self.scope['url_route']['kwargs']['id']).split('_')
        my_id = ids[0]
        other_user_id = ids[1]
        print(other_user_id)
        if int(my_id) > int(other_user_id):
            self.room_name = f'{my_id}-{other_user_id}'
        else:
            self.room_name = f'{other_user_id}-{my_id}'
        
        self.room_group_name = 'privatechat_%s' % self.room_name

        await self.channel_layer.group_add (
            self.room_group_name,
            self.channel_name,
        )

        await self.accept()

    async def disconect(self, code):
        self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )
    
    async def receive(self, text_data = None):
        data = json.loads(text_data)
        message = data['message']
        username = data['username']

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type':'privatechat_message',
                'message': message,
                'username': username
            }
        )

    async def privatechat_message(self, event):
        message = event['message']
        username = event['username']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))