
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
        await self.track_delivery()
        
    async def disconnect(self, close_code):
        """Remove user from WebSocket group."""
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        
    async def track_delivery(self, text_data):
        
        """Simulate real-time delivery movement along a route."""
        
        try:
            order = await self.get_order()
            if not order.route_data:
                return 
            
            route = order.route_data    # JSONField already gives a list
            speed_factor = 2   # Adjust speed (seconds per step)
            
            for i in range(order.current_position_index, len(route)):
                order.current_position_index = i
                order.latitude, order.longitude = route[i]["lat"], route[i]["lng"]

                # Save the order position update (but not in every loop)
                if i % 3 == 0 or i == len(route) - 1:
                    await sync_to_async(order.save)()  # Save every 3 steps
                
                # Broadcast location update via WebSocket
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                       "type": "send_location",
                       "latitude": order.latitude,
                        "longitude": order.longitude,
                    }
                )
                
                # Simulate movement delay
                await asyncio.sleep(speed_factor)
                
        except ObjectDoesNotExist:
            pass
    
    async def send_location(self, event): 
        """Send live location updates to WebSocket clients."""
        await self.send(text_data=json.dumps({
            "latitude": event["latitude"],
            "longitude": event["longitude"],
        }))
        
        #asynchronously fetches the order status from db
    @sync_to_async
    def get_order(self): 
        """Fetch order asynchronously to avoid blocking."""
        from .models import Order
        return Order.objects.get(id=self.order_id)