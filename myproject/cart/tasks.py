from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Order
import time
import logging
from datetime import timedelta


logger = logging.getLogger(__name__)

@shared_task
def update_order_status(order_id):
    """
    Simulate delivery progression with dynamic position updates.
    """
    try:
        order = Order.objects.get(id=order_id)
        channel_layer = get_channel_layer()

        # Delivery route simulation
        route = [
            {"lat": 40.712776, "lng": -74.005974},  # Start
            {"lat": 40.730610, "lng": -73.935242},  # Midway
            {"lat": 40.748817, "lng": -73.985428},  # End
        ]
        statuses = [
            order.Status.PREPARING,
            order.Status.EN_ROUTE,
            order.Status.DELIVERED,
        ]
        eta = 15

        for i, position in enumerate(route):
            # Progress status
            order.status = statuses[i]
            order.eta = order.created_at + timedelta(minutes=eta) if eta > 0 else None
            order.save()

            # Send status and position updates via WebSocket
            async_to_sync(channel_layer.group_send)(
                f'order_{order_id}',
                {
                    'type': 'order_status_update',
                    'status': order.status,
                    'eta': order.eta.isoformat() if order.eta else None,
                    'position': position,
                }
            )

            # Reduce ETA for each step (except Delivered)
            eta -= 5 if i < len(route) - 1 else 0
            time.sleep(10)  # Simulate delivery delay

    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found.")
    except Exception as e:
        logger.error(f"Error in updating order status: {e}")