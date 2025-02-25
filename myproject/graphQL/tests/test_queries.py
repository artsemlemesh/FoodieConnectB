import pytest
from graphene.test import Client
from schema import schema  # Import your GraphQL schema
from cart.models import Order
from reviews.models import Review, Restaurant
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_all_orders_query():
    # Create a test user
    user = User.objects.create_user(username="testuser", password="testpass")

    # Create a test restaurant
    restaurant = Restaurant.objects.create(name="Test Restaurant", description="Test Description", address="Test Address", owner=user)

    # Create some test data
    Order.objects.create(id=1, status=Order.Status.PENDING, user=user, restaurant=restaurant)
    Order.objects.create(id=2, status=Order.Status.DELIVERED, user=user, restaurant=restaurant)

    client = Client(schema)
    query = '''
    query {
        allOrders {
            id
            status
        }
    }
    '''
    executed = client.execute(query)
    assert 'errors' not in executed
    assert len(executed['data']['allOrders']) == 2

@pytest.mark.django_db
def test_pending_reviews_query():
    # Create a test user
    user = User.objects.create_user(username="testuser", password="testpass")

    # Create a test restaurant
    restaurant = Restaurant.objects.create(name="Test Restaurant", description="Test Description", address="Test Address", owner=user)

    # Create some test data
    Review.objects.create(id=1, user=user, restaurant=restaurant, rating=5, comment="Review 1", is_approved=False)
    Review.objects.create(id=2, user=user, restaurant=restaurant, rating=4, comment="Review 2", is_approved=True)

    client = Client(schema)
    query = '''
    query {
        pendingReviews {
            id
            comment
        }
    }
    '''
    executed = client.execute(query)
    assert 'errors' not in executed
    assert len(executed['data']['pendingReviews']) == 1