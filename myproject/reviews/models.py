from django.db import models
from django.contrib.auth import get_user_model
from datetime import datetime

class Review(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)  # Link review to a user
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE, related_name='reviews')  # Link to restaurant
    rating = models.PositiveSmallIntegerField()  # Rating (1-5)
    comment = models.TextField()  # User's review
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when review was created
    is_approved = models.BooleanField(default=False)  # Moderation flag

    def __str__(self):
        return f'{self.user.username} - {self.restaurant.name} - {self.rating}'

# Assuming you already have a Restaurant model
class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return self.name