from celery import shared_task
from datetime import timedelta
from django.utils.timezone import now

import logging

# Set up logging
logger = logging.getLogger(__name__)

@shared_task(name='clean_old_orders')
def clean_old_orders():
    from cart.models import Order # lazy import
    threshold_date = now() - timedelta(days=1)
    old_orders = Order.objects.filter(created_at__lt=threshold_date)
    count = old_orders.count()
    old_orders.delete()
    logger.info(f'Task: clean_old_orders completed | deleted {count} old orders')
    return f"Deleted {count} old orders."