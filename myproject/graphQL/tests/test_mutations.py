# filepath: /Users/mac/Documents/FoodieConnectB/myproject/graphQL/tests/test_mutations.py
import pytest
from graphene.test import Client
from schema import schema  # Import your GraphQL schema
from reviews.models import Restaurant, Review
from cart.models import Product
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_create_restaurant_mutation():
    user = User.objects.create_user(username="testuser", password="testpass")

    client = Client(schema)
    mutation = '''
    mutation {
        createRestaurant(name: "Test Restaurant", description: "Test Description", address: "Test Address", ownerId: "%s") {
            restaurant {
                id
                name
                description
                address
                owner {
                    username
                }
            }
        }
    }
    ''' % user.id
    executed = client.execute(mutation)
    assert 'errors' not in executed
    assert executed['data']['createRestaurant']['restaurant']['name'] == "Test Restaurant"
    assert executed['data']['createRestaurant']['restaurant']['description'] == "Test Description"
    assert executed['data']['createRestaurant']['restaurant']['address'] == "Test Address"
    assert executed['data']['createRestaurant']['restaurant']['owner']['username'] == "testuser"

@pytest.mark.django_db
def test_create_product_mutation():
    client = Client(schema)
    mutation = '''
    mutation {
        createProduct(name: "Test Product", price: 10, description: "Test Description", category: "Test Category") {
            product {
                id
                name
                price
                description
                category
            }
        }
    }
    '''
    executed = client.execute(mutation)
    assert 'errors' not in executed
    assert executed['data']['createProduct']['product']['name'] == "Test Product"
    assert executed['data']['createProduct']['product']['price'] == "10"
    assert executed['data']['createProduct']['product']['description'] == "Test Description"
    assert executed['data']['createProduct']['product']['category'] == "Test Category"

@pytest.mark.django_db
def test_approve_review_mutation():
    user = User.objects.create_user(username="testuser", password="testpass")
    restaurant = Restaurant.objects.create(name="Test Restaurant", description="Test Description", address="Test Address", owner=user)
    review = Review.objects.create(user=user, restaurant=restaurant, rating=5, comment="Great!", is_approved=False)

    client = Client(schema)
    mutation = '''
    mutation {
        approveReview(reviewId: "%s") {
            success
            message
            review {
                id
                isApproved
            }
        }
    }
    ''' % review.id
    executed = client.execute(mutation)
    assert 'errors' not in executed
    assert executed['data']['approveReview']['success'] is True
    assert executed['data']['approveReview']['message'] == "Review approved successfully."
    assert executed['data']['approveReview']['review']['isApproved'] is True