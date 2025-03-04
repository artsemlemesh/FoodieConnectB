from celery import shared_task
from datetime import timedelta
from django.utils.timezone import now
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Order
import logging
import json

logger = logging.getLogger(__name__)

@shared_task
def update_delivery_location(order_id):
    """
    Moves the delivery one step along the predefined route and schedules the next movement.
    """
    try:
        order = Order.objects.get(id=order_id)

        # Ensure route_data is a valid list
        if isinstance(order.route_data, str):  
            order.route_data = json.loads(order.route_data)

        if not order.route_data or order.current_position_index >= len(order.route_data) - 1:
            logger.warning(f"Order {order_id} has no route data or is already delivered.")
            order.status = "DELIVERED"
            order.eta = None
            order.save()
            return

        # Move to the next position
        next_index = order.current_position_index + 1
        position = order.route_data[next_index]  
        order.current_position_index = next_index
        order.status = "EN_ROUTE" if next_index < len(order.route_data) - 1 else "DELIVERED"
        order.eta = now() + timedelta(minutes=5 * (len(order.route_data) - next_index - 1)) if next_index < len(order.route_data) - 1 else None
        order.save()

        # Send live update via WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"order_{order_id}",
            {
                "type": "send_location",
                "status": order.status,
                "eta": order.eta.isoformat() if order.eta else None,
                "latitude": position[0],
                "longitude": position[1],
                "current_position_index": order.current_position_index,
            },
        )

        # Schedule the next movement if not yet delivered
        if order.status != "DELIVERED":
            update_delivery_location.apply_async((order_id,), countdown=5)  # Runs after 5 sec


    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found.")
    except Exception as e:
        logger.error(f"Error in update_delivery_location: {e}")