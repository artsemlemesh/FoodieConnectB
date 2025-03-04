from rest_framework import serializers
from .models import Order
from reviews.serializers import RestaurantSerializer

class OrderSerializer(serializers.ModelSerializer):
    route_data = serializers.JSONField()  # Ensure route data is serialized properly
    restaurant = RestaurantSerializer(read_only=True)  # Nested serializer

    class Meta:
        model = Order
        fields = "__all__"
        
    def get_restaurant(self, obj):
        """Return restaurant location if available."""
        if obj.restaurant:
            return {
                'latitude': obj.restaurant.latitude,
                'longitude': obj.restaurant.longitude,
            }
        return None