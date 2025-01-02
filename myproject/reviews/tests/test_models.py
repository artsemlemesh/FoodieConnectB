import pytest
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from reviews.models import Review, Restaurant

User = get_user_model()

@pytest.fixture
def create_user(db):
    """Fixture to create a user"""
    def _create_user(username, email):
        return User.objects.create_user(username=username, email=email, password="password123")
    return _create_user

@pytest.fixture
def create_restaurant(create_user, db):
    """Fixture to create a restaurant"""
    def _create_restaurant(name, description, address, owner):
        return Restaurant.objects.create(
            name=name,
            description=description,
            address=address,
            owner=owner
        )
    return _create_restaurant

@pytest.fixture
def create_review(create_user, create_restaurant, db):
    """Fixture to create a review"""
    def _create_review(user, restaurant, rating, comment):
        return Review.objects.create(
            user=user,
            restaurant=restaurant,
            rating=rating,
            comment=comment
        )
    return _create_review


@pytest.mark.django_db
def test_create_restaurant(create_user, create_restaurant):
    """Test creating a restaurant"""
    user = create_user("testowner", "owner@example.com")
    restaurant = create_restaurant("Test Restaurant", "Great food", "123 Test St", user)

    assert restaurant.name == "Test Restaurant"
    assert restaurant.description == "Great food"
    assert restaurant.address == "123 Test St"
    assert restaurant.owner == user
    assert str(restaurant) == f"{restaurant.name} - {user}"


@pytest.mark.django_db
def test_create_review(create_user, create_restaurant, create_review):
    """Test creating a review"""
    user = create_user("testuser", "user@example.com")
    owner = create_user("testowner", "owner@example.com")
    restaurant = create_restaurant("Test Restaurant", "Great food", "123 Test St", owner)
    review = create_review(user, restaurant, 5, "Excellent food!")

    assert review.user == user
    assert review.restaurant == restaurant
    assert review.rating == 5
    assert review.comment == "Excellent food!"
    assert review.is_approved is False
    assert str(review) == f"{user.username} - {restaurant.name} - {review.rating}"


@pytest.mark.django_db
def test_review_cannot_be_created_without_required_fields(create_user, create_restaurant):
    """Test that a review cannot be created without required fields"""
    user = create_user("testuser", "user@example.com")
    owner = create_user("testowner", "owner@example.com")
    restaurant = create_restaurant("Test Restaurant", "Great food", "123 Test St", owner)

    with pytest.raises(IntegrityError):
        Review.objects.create(user=user, restaurant=restaurant, rating=None, comment="No rating provided")


@pytest.mark.django_db
def test_restaurant_has_reviews(create_user, create_restaurant, create_review):
    """Test that a restaurant can have multiple reviews"""
    user1 = create_user("testuser1", "user1@example.com")
    user2 = create_user("testuser2", "user2@example.com")
    owner = create_user("testowner", "owner@example.com")
    restaurant = create_restaurant("Test Restaurant", "Great food", "123 Test St", owner)

    review1 = create_review(user1, restaurant, 4, "Good food")
    review2 = create_review(user2, restaurant, 5, "Amazing food")

    assert restaurant.reviews.count() == 2
    assert review1 in restaurant.reviews.all()
    assert review2 in restaurant.reviews.all()