from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Order
import time


@shared_task
def update_order_status(order_id):
    print('TASK update_order_status')
    order = Order.objects.get(id=order_id)
    channel_layer = get_channel_layer()
    print('ORDER', order)

    #sequence of statuses
    statuses = [
        ('Preparing', None),
        ('En Route', order.update_eta(15)),
        ('Delivered', None)
    ]

    for status, _ in statuses:
        time.sleep(10) #simulates time delay for status changes
        order.status = status
        order.save()

        async_to_sync(channel_layer.group_send)(
            f'order_{order_id}',
            {
                'type': 'order_status_update',
                'status': status,
                'eta': order.eta.isoformat() if order.eta else None,
                'message': status
            }
        )