import pytest
from rest_framework.test import APIClient
from rest_framework import status
from reviews.models import Review, Restaurant
from cart.models import Order


@pytest.fixture
def api_client():
    """Fixture for DRF's test client."""
    return APIClient()


@pytest.fixture
def create_user(db, django_user_model):
    """Fixture to create a user."""
    def _create_user(username, email):
        return django_user_model.objects.create_user(username=username, email=email, password="password123")
    return _create_user


@pytest.fixture
def authenticated_client(api_client, create_user):
    """Fixture for an authenticated API client."""
    user = create_user("testuser", "user@example.com")
    api_client.force_authenticate(user=user)
    return api_client, user


@pytest.fixture
def create_restaurant(create_user):
    """Fixture to create a restaurant."""
    def _create_restaurant(name, description, address, owner):
        return Restaurant.objects.create(name=name, description=description, address=address, owner=owner)
    return _create_restaurant


@pytest.fixture
def create_review(create_user, create_restaurant):
    """Fixture to create a review."""
    def _create_review(user, restaurant, rating, comment, is_approved=False):
        return Review.objects.create(
            user=user, restaurant=restaurant, rating=rating, comment=comment, is_approved=is_approved
        )
    return _create_review


@pytest.mark.django_db
def test_create_review(authenticated_client, create_restaurant):
    """Test creating a review."""
    api_client, user = authenticated_client
    owner = user
    restaurant = create_restaurant("Test Restaurant", "Description", "123 Test St", owner)

    data = {
        "restaurant": restaurant.id,
        "rating": 5,
        "comment": "Amazing place!",
    }

    response = api_client.post("/reviews/reviews/create/", data)
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()

    assert response_data["rating"] == 5
    assert response_data["comment"] == "Amazing place!"
    assert response_data["user"] == user.id
    assert response_data["restaurant"] == restaurant.id


@pytest.mark.django_db
def test_list_reviews(api_client, create_restaurant, create_review, create_user):
    """Test listing reviews for a restaurant."""
    owner = create_user(username="restaurant_owner2", email='mike@gmail.com')
    restaurant = create_restaurant("Test Restaurant", "Description", "123 Test St", owner)
    create_review(owner, restaurant, 5, "Amazing place!", is_approved=True)
    create_review(owner, restaurant, 4, "Good food!", is_approved=False)

    response = api_client.get(f"/reviews/reviews/{restaurant.id}/")
    assert response.status_code == status.HTTP_200_OK
    reviews = response.json()

    assert len(reviews) == 1  # Only approved reviews should be listed
    assert reviews[0]["comment"] == "Amazing place!"


@pytest.mark.django_db
def test_restaurant_list(api_client, create_restaurant, create_user):
    """Test listing all restaurants."""
    owner = create_user(username="restaurant_owner1", email='joew@gmail.com')
    create_restaurant("Test Restaurant 1", "Description 1", "Address 1", owner)
    create_restaurant("Test Restaurant 2", "Description 2", "Address 2", owner)

    response = api_client.get("/reviews/restaurants/")
    assert response.status_code == status.HTTP_200_OK
    restaurants = response.json()

    assert len(restaurants) == 2
    assert restaurants[0]["name"] == "Test Restaurant 1"
    assert restaurants[1]["name"] == "Test Restaurant 2"


@pytest.mark.django_db
def test_restaurant_detail(api_client, create_restaurant, create_user):
    """Test fetching a restaurant's details."""
    owner = create_user(username="restaurant_owner", email='joe@gmail.com')
    restaurant = create_restaurant("Test Restaurant", "Description", "123 Test St", owner)

    response = api_client.get(f"/reviews/restaurants/{restaurant.id}/")
    assert response.status_code == status.HTTP_200_OK
    restaurant_data = response.json()

    assert restaurant_data["name"] == "Test Restaurant"
    assert restaurant_data["description"] == "Description"
    assert restaurant_data["address"] == "123 Test St"


@pytest.mark.django_db
def test_dashboard_data(authenticated_client):
    """Test dashboard data aggregation."""
    api_client, user = authenticated_client
    Order.objects.create(user=user, total_amount=100.50)
    Order.objects.create(user=user, total_amount=200.75)

    response = api_client.get("/reviews/dashboard/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["orders_count"] == 2
    assert data["total_revenue"] == 301.25


@pytest.mark.django_db
def test_restaurant_reviews(authenticated_client, create_restaurant, create_review):
    """Test listing all reviews for a restaurant."""
    api_client, user = authenticated_client
    restaurant = create_restaurant("Test Restaurant", "Description", "123 Test St", user)
    create_review(user, restaurant, 5, "Great place!", is_approved=True)
    create_review(user, restaurant, 3, "Not bad.", is_approved=False)

    response = api_client.get(f"/reviews/restaurants/{restaurant.id}/reviews/")
    assert response.status_code == status.HTTP_200_OK
    reviews = response.json()

    assert len(reviews) == 2
    assert reviews[0]["comment"] == "Not bad."
    assert reviews[1]["comment"] == "Great place!"