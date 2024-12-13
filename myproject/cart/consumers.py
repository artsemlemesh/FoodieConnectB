from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async

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

        # Send initial order state
        await self.send_order_update()

    async def send_order_update(self):
        """
        Fetch and send current order state
        """
        from .models import Order # Import here to avoid circular import
        order = await database_sync_to_async(Order.objects.get)(id=self.order_id)
        await self.send(text_data=json.dumps({
            "status": order.status,
            "eta": order.eta.isoformat() if order.eta else None,
            "position": {"lat": 40.712776, "lng": -74.005974},  # Default position

        }))

    async def order_status_update(self, event):
        """
        Handle incoming status updates
        """
        status = event.get("status")
        eta = event.get("eta")
        position = event.get("position")
        if status:
            await self.send(text_data=json.dumps({
            "status": status,
            "eta": eta,
            "position": position,

        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.order_group_name,
            self.channel_name
        )