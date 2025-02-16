import graphene
from graphene_django.types import DjangoObjectType
from reviews.models import Restaurant, Review
from django.contrib.auth import get_user_model
from cart.models import Order, Product
from django.conf import settings
from graphene import relay
from base64 import b64encode

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


class ProductFilterInput(graphene.InputObjectType):
    # name = graphene.String()
    category = graphene.String()
    # min_price = graphene.Float(name="min_price")
    # max_price = graphene.Float(name="max_price")


class PageInfo(graphene.ObjectType):
    has_next_page = graphene.Boolean()
    end_cursor = graphene.String()

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'description', 'photo', 'category')
        interfaces = (graphene.relay.Node,) #this is for large datasets, set up later

    def resolve_photo(self, info):
        if self.photo:
            return f'{settings.MEDIA_URL}{self.photo}'
        return None


class ProductConnection(graphene.Connection):
    class Meta:
        node = ProductType

    # @staticmethod
    # def resolve_cursor_for_node(node, *_):
    #     cursor = f"arrayconnection:{node.id}"
    #     encoded_cursor = b64encode(cursor.encode()).decode()
    #     print(f"Generated cursor: {encoded_cursor}")  # Debug
    #     return encoded_cursor
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
    

