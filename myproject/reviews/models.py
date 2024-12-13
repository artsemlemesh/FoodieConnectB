from django.db import models
from django.contrib.auth import get_user_model

class Review(models.Model):
    user = models.ForeignKey(get_user_model(), null=False, on_delete=models.CASCADE)  # Link review to a user
    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE, related_name='reviews')  # Link to restaurant
    rating = models.PositiveSmallIntegerField()  # Rating (1-5)
    comment = models.TextField()  # User's review
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when review was created
    is_approved = models.BooleanField(default=False)  # Moderation flag

    def __str__(self):
        return f'{self.user.username} - {self.restaurant.name} - {self.rating}'


class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(default="")
    address = models.TextField()
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name