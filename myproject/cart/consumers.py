from channels.generic.websocket import AsyncWebsocketConsumer
import json

class OrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        self.order_group_name = f'order_{self.order_id}'

        # Join the order group
        await self.channel_layer.group_add(
            self.order_group_name,
            self.channel_name
        )

        # Accept the connection
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the order group
        await self.channel_layer.group_discard(
            self.order_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Handle incoming WebSocket data
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            self.order_group_name,
            {
                'type': 'order_status_update',
                'message': data.get('message', ''),
            }
        )

    async def order_status_update(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message']
        }))
        # daphne -b 0.0.0.0 -p 8000 myproject.asgi:application