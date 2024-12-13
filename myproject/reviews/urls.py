from django.urls import path
from .views import (
    ListReviewsView,
    CreateReviewView,
    DashboardDataView,
    RestaurantListView,
    RestaurantDetailView,
    RestaurantReviewsView,
)

app_name = 'reviews'

urlpatterns = [
    # Restaurant-related routes
    path('restaurants/', RestaurantListView.as_view(), name='restaurant-list'),  # List all restaurants
    path('restaurants/<int:pk>/', RestaurantDetailView.as_view(), name='restaurant-detail'),  # Single restaurant details
    path('restaurants/<int:pk>/reviews/', RestaurantReviewsView.as_view(), name='restaurant-reviews'),  # Reviews for a specific restaurant

    # Review-related routes
    path('reviews/create/', CreateReviewView.as_view(), name='review-create'),  # Create a review
    path('reviews/<int:restaurant_id>/', ListReviewsView.as_view(), name='review-list'),  # List reviews for a restaurant

    # Dashboard route
    path('dashboard/', DashboardDataView.as_view(), name='dashboard-data'),  # Admin/User dashboard data
]