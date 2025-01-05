import graphene
from graphene_django.types import DjangoObjectType
from reviews.models import Restaurant, Review
from django.contrib.auth import get_user_model
from cart.models import Order, Product

class ReviewType(DjangoObjectType):
    class Meta:
        model = Review
        fields = ('id', 'user', 'rating', 'restaurant', 'comment', 'is_approved')

class RestaurantType(DjangoObjectType):
    reviews = graphene.List(ReviewType)

    class Meta:
        model = Restaurant
        fields = ('id', 'name', 'description', 'address', 'owner', 'reviews')

    def resolve_reviews(self, info):
        return self.reviews.filter(is_approved=True)

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'description', 'photo', 'category')


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'email')

class OrderType(DjangoObjectType):
    user = graphene.Field(UserType)
    restaurant = graphene.Field(RestaurantType)
    created_at = graphene.String()

    class Meta:
        model = Order
        fields = ('id', 'user', 'created_at', 'status', 'total_amount', 'eta', 'restaurant')

    def resolve_user(self, info):
        return self.user

    def resolve_restaurant(self, info):
        return self.restaurant

    def resolve_created_at(self, info):
        return self.created_at.strftime("%Y-%m-%d %H:%M:%S")
    

