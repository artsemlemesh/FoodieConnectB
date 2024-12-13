from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # Display username in responses

    class Meta:
        model = Review
        fields = ['id', 'user', 'restaurant', 'rating', 'comment', 'created_at', 'is_approved']
        read_only_fields = ['id', 'user', 'created_at', 'is_approved']  # Certain fields should not be editable