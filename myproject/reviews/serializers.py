from rest_framework import serializers
from .models import Review,  Restaurant

class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = ['id', 'user', 'restaurant', 'rating', 'comment', 'created_at', 'is_approved']

    

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'description', 'owner', 'created_at']


