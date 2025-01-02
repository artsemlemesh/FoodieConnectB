import pytest
from rest_framework.exceptions import ValidationError
from reviews.models import Review, Restaurant
from reviews.serializers import ReviewSerializer, RestaurantSerializer


@pytest.fixture
def create_user(db, django_user_model):
    """Fixture to create a user."""
    def _create_user(username, email):
        return django_user_model.objects.create_user(username=username, email=email, password="password123")
    return _create_user


@pytest.fixture
def create_restaurant(create_user, db):
    """Fixture to create a restaurant."""
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
    """Fixture to create a review."""
    def _create_review(user, restaurant, rating, comment):
        return Review.objects.create(
            user=user,
            restaurant=restaurant,
            rating=rating,
            comment=comment
        )
    return _create_review


@pytest.mark.django_db
def test_review_serializer_serialization(create_user, create_restaurant, create_review):
    """Test serialization of a Review."""
    user = create_user("testuser", "user@example.com")
    owner = create_user("testowner", "owner@example.com")
    restaurant = create_restaurant("Test Restaurant", "Great food", "123 Test St", owner)
    review = create_review(user, restaurant, 5, "Excellent food!")

    serializer = ReviewSerializer(instance=review)
    serialized_data = serializer.data

    assert serialized_data["id"] == review.id
    assert serialized_data["user"] == review.user.id
    assert serialized_data["restaurant"] == review.restaurant.id
    assert serialized_data["rating"] == 5
    assert serialized_data["comment"] == "Excellent food!"
    assert serialized_data["is_approved"] == review.is_approved


@pytest.mark.django_db
def test_review_serializer_deserialization(create_user, create_restaurant):
    """Test deserialization and validation of a Review."""
    user = create_user("testuser", "user@example.com")
    owner = create_user("testowner", "owner@example.com")
    restaurant = create_restaurant("Test Restaurant", "Great food", "123 Test St", owner)

    data = {
        "user": user.id,
        "restaurant": restaurant.id,
        "rating": 4,
        "comment": "Nice place!",
        "is_approved": True,
    }
    serializer = ReviewSerializer(data=data)
    assert serializer.is_valid()
    review = serializer.save()

    assert review.user == user
    assert review.restaurant == restaurant
    assert review.rating == 4
    assert review.comment == "Nice place!"
    assert review.is_approved is True


# @pytest.mark.django_db
# def test_review_serializer_invalid_rating(create_user, create_restaurant):
#     """Test validation for invalid rating in ReviewSerializer."""
#     user = create_user("testuser", "user@example.com")
#     owner = create_user("testowner", "owner@example.com")
#     restaurant = create_restaurant("Test Restaurant", "Great food", "123 Test St", owner)

#     data = {
#         "user": user.id,
#         "restaurant": restaurant.id,
#         "rating": 6,  # Invalid rating
#         "comment": "Too good!",
#     }
#     serializer = ReviewSerializer(data=data)
#     assert not serializer.is_valid()
#     assert "rating" in serializer.errors


@pytest.mark.django_db
def test_restaurant_serializer_serialization(create_user, create_restaurant, rf):
    """Test serialization of a Restaurant."""
    owner = create_user("testowner", "owner@example.com")
    restaurant = create_restaurant("Test Restaurant", "Great food", "123 Test St", owner)

    request = rf.get("/")
    serializer = RestaurantSerializer(instance=restaurant, context={"request": request})
    serialized_data = serializer.data

    assert serialized_data["id"] == restaurant.id
    assert serialized_data["name"] == "Test Restaurant"
    assert serialized_data["description"] == "Great food"
    assert serialized_data["address"] == "123 Test St"
    assert serialized_data["owner"] == restaurant.owner.id
    assert serialized_data["photo"] is None  # No photo provided


@pytest.mark.django_db
def test_restaurant_serializer_photo_url(create_user, create_restaurant, rf):
    """Test absolute URL generation for restaurant photo."""
    owner = create_user("testowner", "owner@example.com")
    restaurant = create_restaurant("Test Restaurant", "Great food", "123 Test St", owner)
    restaurant.photo = "restaurants/test_photo.jpg"
    restaurant.save()

    request = rf.get("/")
    serializer = RestaurantSerializer(instance=restaurant, context={"request": request})
    serialized_data = serializer.data

    assert serialized_data["photo"] == request.build_absolute_uri(restaurant.photo.url)