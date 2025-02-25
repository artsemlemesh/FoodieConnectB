# filepath: /Users/mac/Documents/FoodieConnectB/myproject/graphQL/tests/test_types.py
import pytest
from graphene.test import Client
from reviews.models import Restaurant, Review
from cart.models import Order, Product
from django.contrib.auth import get_user_model
from schema import schema  # Adjust the import path as necessary

User = get_user_model()

@pytest.mark.django_db
def test_pending_reviews_query():
    user = User.objects.create_user(username="testuser", password="testpass")
    restaurant = Restaurant.objects.create(name="Test Restaurant", description="Test Description", address="Test Address", owner=user)
    review = Review.objects.create(user=user, restaurant=restaurant, rating=5, comment="Great!", is_approved=False)

    client = Client(schema)
    query = '''
    query GetReviews {
        pendingReviews {
            id
            user {
                username
            }
            restaurant {
                name
            }
            rating
            comment
            isApproved
        }
    }
    '''
    executed = client.execute(query)
    print(executed)  # Debugging statement to print the response
    assert 'errors' not in executed
    assert len(executed['data']['pendingReviews']) > 0  # Ensure there is at least one pending review
    assert executed['data']['pendingReviews'][0]['user']['username'] == "testuser"
    assert executed['data']['pendingReviews'][0]['restaurant']['name'] == "Test Restaurant"
    assert executed['data']['pendingReviews'][0]['rating'] == 5
    assert executed['data']['pendingReviews'][0]['comment'] == "Great!"
    assert executed['data']['pendingReviews'][0]['isApproved'] is False
    
@pytest.mark.django_db
def test_product_type():
    product = Product.objects.create(name="Test Product", price=10.99, description="Test Description", category="Test Category")

    client = Client(schema)
    query = '''
    query {
        allProducts {
            edges {
                node {
                    id
                    name
                    price
                    description
                    category
                }
            }
        }
    }
    '''
    executed = client.execute(query)
    print(executed)  # Debugging statement to print the response
    assert 'errors' not in executed
    assert len(executed['data']['allProducts']['edges']) > 0  # Ensure there is at least one product
    assert executed['data']['allProducts']['edges'][0]['node']['name'] == "Test Product"
    assert executed['data']['allProducts']['edges'][0]['node']['price'] == "10.99"
    assert executed['data']['allProducts']['edges'][0]['node']['description'] == "Test Description"
    assert executed['data']['allProducts']['edges'][0]['node']['category'] == "Test Category"

@pytest.mark.django_db
def test_order_type():
    user = User.objects.create_user(username="testuser", password="testpass")
    restaurant = Restaurant.objects.create(name="Test Restaurant", description="Test Description", address="Test Address", owner=user)
    order = Order.objects.create(user=user, restaurant=restaurant, status="PENDING", total_amount=100)

    client = Client(schema)
    query = '''
    query {
        allOrders {
            id
            user {
                username
            }
            restaurant {
                name
            }
            status
            totalAmount
        }
    }
    '''
    executed = client.execute(query)
    assert 'errors' not in executed
    assert executed['data']['allOrders'][0]['user']['username'] == "testuser"
    assert executed['data']['allOrders'][0]['restaurant']['name'] == "Test Restaurant"
    assert executed['data']['allOrders'][0]['status'] == "PENDING"
    assert executed['data']['allOrders'][0]['totalAmount'] == "100.00"