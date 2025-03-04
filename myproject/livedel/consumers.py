
import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.exceptions import ObjectDoesNotExist
# from .models import Order
from asgiref.sync import sync_to_async

class LiveDeliveryConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Join the WebSocket group and start movement simulation."""
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        self.group_name = f'order_{self.order_id}'
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        
        # Start simulating movement when a user connects
        # await self.track_delivery()
        
    async def disconnect(self, close_code):
        """Remove user from WebSocket group."""
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        

    
    async def send_location(self, event): 
        """Send live location updates to WebSocket clients."""
        await self.send(text_data=json.dumps({
            "latitude": event["latitude"],
            "longitude": event["longitude"],
            "current_position_index": event["current_position_index"],
            "status": event["status"],
            "eta": event["eta"],
        }))
        
        #asynchronously fetches the order status from db
    @sync_to_async
    def get_order(self): 
        """Fetch order asynchronously to avoid blocking."""
        from .models import Order
        return Order.objects.get(id=self.order_id)