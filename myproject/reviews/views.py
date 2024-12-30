from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Review, Restaurant
from .serializers import ReviewSerializer, RestaurantSerializer
from cart.models import Order

class CreateReviewView(APIView):
    """
    Handles review creation for a specific restaurant
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print(f"Authenticated user: {request.user}") 
        print(f"Request data: {request.data}")  # Debug input data
        data = request.data
        data['user'] = request.user.id # automatically set the user to the logged-in user
        
        serializer = ReviewSerializer(data=data, context={'request': request})

        if serializer.is_valid():
            print("Serializer valid.")  # Debug serializer state
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(f"Serializer errors: {serializer.errors}")  # Debug serializer errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ListReviewsView(APIView):
    """
    List all approved reviews for a given restaurant
    """
    def get(self, request, restaurant_id):
        reviews = Review.objects.filter(restaurant_id=restaurant_id, is_approved=True).order_by('-created_at')
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    

class RestaurantListView(APIView):
    """
    List all restaurants
    """
    def get(self, request):
        restaurants = Restaurant.objects.all()
        serializer = RestaurantSerializer(restaurants, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class RestaurantDetailView(APIView):
    """
    Fetch details of a single restaurant by ID
    """
    def get(self, request, pk):
        try:
            restaurant = Restaurant.objects.get(pk=pk)
            serializer = RestaurantSerializer(restaurant)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Restaurant.DoesNotExist:
            return Response({"error": "Restaurant not found"}, status=status.HTTP_404_NOT_FOUND)


class DashboardDataView(APIView):
    """
    Aggregate data for dashboard metrics (e.g., total orders, revenue)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Fetch all orders associated with the logged-in user
        orders = Order.objects.all()

        # Calculate total orders and revenue
        orders_count = orders.count()
        total_revenue = sum(order.total_amount for order in orders)
        
        # Return aggregated data
        return Response({
            'orders_count': orders_count,
            'total_revenue': total_revenue,
        })



class RestaurantReviewsView(APIView):
    """
    List all reviews for a restaurant (approved and unapproved)
    """
    permission_classes = [IsAuthenticated]  # Optional, based on whether non-auth users should view

    def get(self, request, pk):
        reviews = Review.objects.filter(restaurant_id=pk).order_by('-created_at')
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)