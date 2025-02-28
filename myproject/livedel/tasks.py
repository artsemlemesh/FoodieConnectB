from celery import shared_task
import time
from datetime import timedelta
from django.utils.timezone import now
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Order
import logging

logger = logging.getLogger(__name__)

@shared_task
def update_delivery_location(order_id):
    """
    Move the delivery along the predefined route in real-time.
    """
    try:
        order = Order.objects.get(id=order_id)
        channel_layer = get_channel_layer()

        if not order.route_data or order.current_position_index >= len(order.route_data):
            logger.warning(f"Order {order_id} has no route data or already delivered.")
            return

        for i in range(order.current_position_index, len(order.route_data)):
            position = order.route_data[i]  # Get the next coordinate
            order.latitude = position["lat"]
            order.longitude = position["lng"]
            order.current_position_index = i
            order.status = "EN_ROUTE" if i < len(order.route_data) - 1 else "DELIVERED"
            order.eta = now() + timedelta(minutes=5 * (len(order.route_data) - i - 1)) if i < len(order.route_data) - 1 else None
            order.save()

            # Send live update via WebSocket
            async_to_sync(channel_layer.group_send)(
                f"order_{order_id}",
                {
                    "type": "order_status_update",
                    "status": order.status,
                    "eta": order.eta.isoformat() if order.eta else None,
                    "latitude": order.latitude,
                    "longitude": order.longitude,
                },
            )

            # Simulate movement delay
            time.sleep(10)

        logger.info(f"Order {order_id} delivery completed.")

    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found.")
    except Exception as e:
        logger.error(f"Error in update_delivery_location: {e}")