from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Order, CartItem
import logging

logger = logging.getLogger(__name__)



@receiver(post_save, sender=Order)
def clear_cart_after_purchase(sender, instance, **kwargs):
    if instance.status == Order.Status.PAID:
        deleted_count, _ = CartItem.objects.filter(user=instance.user).delete()
        logger.info(f"Cleared {deleted_count} items from the cart for user {instance.user.id}.")

