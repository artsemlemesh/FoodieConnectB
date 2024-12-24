import graphene
from graphene_django.types import DjangoObjectType
from cart.models import Order
from reviews.models import Restaurant
from django.contrib.auth import get_user_model



class RestaurantType(DjangoObjectType):
    class Meta:
        model = Restaurant
        fields = ('name', 'description', 'address', 'owner')

class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'email')

class OrderType(DjangoObjectType):
    user = graphene.Field(UserType)
    restaurant = graphene.Field(RestaurantType)

    class Meta:
        model = Order
        fields = ('id', 'user', 'created_at', 'status', 'total_amount', 'eta', 'restaurant')

    def resolve_user(self, info):
        # Return the related user object
        return self.user

class Query(graphene.ObjectType):
    all_orders = graphene.List(OrderType)

    def resolve_all_orders(root, info):
        return Order.objects.all()
    

schema = graphene.Schema(query=Query)
