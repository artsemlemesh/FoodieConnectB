from django.db import models
from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import timedelta

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    photo = models.ImageField(upload_to='products/')
    category = models.CharField(max_length=50, default='General')  # Added category field
    
    def __str__(self):
        return self.name
    

class CartItem(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
    

class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Preparing', 'Preparing'),
        ('En Route', 'En Route'),
        ('Delivered', 'Delivered'),
    ]

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )
    eta = models.DateTimeField(null=True, blank=True)  # Estimated time of arrival


    def __str__(self):
        return f'Order {self.id} - {self.status}'
    
    def update_eta(self, minutes=15):
        self.eta = self.created_at + timedelta(minutes=minutes)
        self.save()

    def save(self, *args, **kwargs):
        # Check if the status has changed
        if self.pk:  # Ensure this is an update, not a new object
            old_status = Order.objects.filter(pk=self.pk).values_list('status', flat=True).first()
            if old_status and old_status != self.status:
                # Send WebSocket message to the group
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'order_{self.id}',  # Group name
                    {'type': 'order_status_update', 'message': self.status}
                )
        super().save(*args, **kwargs)


class OrderItem(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"
    

# from cart.models import Order

# order = Order.objects.get(id=1)  
# order.status = 'En Route'  
# order.save()  