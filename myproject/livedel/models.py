from django.db import models
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from datetime import timedelta
import json
import requests
from django.contrib.auth import get_user_model
from reviews.models import Restaurant

#optimize route fetching with caching
from django.core.cache import cache

class Order(models.Model):
    class Status(models.TextChoices):
        PAID = 'Paid', 'Paid'
        PENDING = 'Pending', 'Pending'
        PREPARING = 'Preparing', 'Preparing'
        EN_ROUTE = 'En Route', 'En Route'
        DELIVERED = 'Delivered', 'Delivered'

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='live_orders')
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(
        max_length=20,
        choices=Status.choices, 
        default=Status.PENDING
    )
    eta = models.DateTimeField(null=True, blank=True)  # Estimated time of arrival
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True, blank=True, related_name='liveorders')

    # Delivery tracking fields
    latitude = models.FloatField(null=True, blank=True)  # Customer's delivery latitude
    longitude = models.FloatField(null=True, blank=True)  # Customer's delivery longitude
    route_data = models.JSONField(null=True, blank=True)  # Stores route coordinates (from OpenStreetMap API)
    current_position_index = models.IntegerField(default=0)  # Keeps track of where the delivery is on the route

    def progress_status(self):
        status_progression = [
            self.Status.PAID,
            self.Status.PENDING,
            self.Status.PREPARING,
            self.Status.EN_ROUTE,
            self.Status.DELIVERED
        ]
        
        if self.status == self.Status.DELIVERED:
            return self.status  # No progression beyond 'Delivered'

        current_index = status_progression.index(self.status)
        if current_index < len(status_progression) - 1:
            next_status = status_progression[current_index + 1]
            self.status = next_status
            if next_status == self.Status.EN_ROUTE:
                self.update_eta(15)
                self.fetch_route()  # Fetch route once delivery starts
            else:
                self.eta = None
            self.save()
            return self.status
        return self.status
    
    
    def __str__(self):
        return f'Order {self.id} - {self.status}'

    def update_eta(self, minutes=15):
        self.eta = now() + timedelta(minutes=minutes)
        self.save()

    def fetch_route(self):
        """
        Calls OpenStreetMap API to get route from restaurant to delivery location.
        """
        if not self.restaurant or not self.delivery_location:
            raise ValidationError("Restaurant and delivery location must be set.")

        cache_key = f"route_{self.restaurant.id}_{self.id}"
        cached_route = cache.get(cache_key)
        
        if cached_route:
            self.route_data = cached_route
        else:
            osrm_url = f"http://router.project-osrm.org/route/v1/driving/{self.restaurant.longitude},{self.restaurant.latitude};{self.delivery_location.x},{self.delivery_location.y}?overview=full&geometries=geojson"
            
            response = requests.get(osrm_url)
            if response.status_code == 200:
                route_data = response.json().get("routes", [])[0].get("geometry", {}).get("coordinates", [])
                self.route_data = json.dumps(route_data)  # Store as JSON
                cache.set(cache_key, self.route_data, timeout=60 * 60) #cache for 1 hour
        self.current_position_index = 0  # Reset position
        self.save()