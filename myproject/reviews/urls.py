from django.urls import path
from .views import ListReviewsView, CreateReviewView

app_name = 'reviews'

urlpatterns = [
    path('reviews/<int:restaurant_id>/', ListReviewsView.as_view(), name='list-reviews'),
    path('reviews/create/', CreateReviewView.as_view(), name='create-review'),
]