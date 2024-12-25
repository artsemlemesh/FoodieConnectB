import graphene
from .types import RestaurantType
from reviews.models import Restaurant
from django.contrib.auth import get_user_model
from graphql import GraphQLError  # Better error handling


class CreateRestaurant(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String(required=True)
        address = graphene.String(required=True)
        owner_id = graphene.ID(required=True)  # Use ID for consistency

    restaurant = graphene.Field(RestaurantType)

    def mutate(self, info, name, description, address, owner_id):
        # Validate owner existence
        try:
            user = get_user_model().objects.get(id=owner_id)
        except get_user_model().DoesNotExist:
            raise GraphQLError('The specified owner does not exist.')

        # Create and save the restaurant
        restaurant = Restaurant(
            name=name,
            description=description,
            address=address,
            owner=user
        )
        restaurant.save()

        return CreateRestaurant(restaurant=restaurant)


class Mutation(graphene.ObjectType):
    create_restaurant = CreateRestaurant.Field()