from rest_framework import serializers
from .models import Review,  Restaurant

class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = ['id', 'user', 'restaurant', 'rating', 'comment', 'created_at', 'is_approved']

    

class RestaurantSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'description','address', 'owner', 'created_at', 'photo']

    #to return absolute path for photos
    def get_photo(self, obj):
        request = self.context.get('request')
        if obj.photo and request:
            return request.build_absolute_uri(obj.photo.url)
        return None
