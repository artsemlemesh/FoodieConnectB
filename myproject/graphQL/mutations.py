import graphene
from .types import RestaurantType, ProductType
from reviews.models import Restaurant
from cart.models import Product
from django.contrib.auth import get_user_model
from graphql import GraphQLError
from graphene_file_upload.scalars import Upload


class CreateRestaurant(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String(required=True)
        address = graphene.String(required=True)
        owner_id = graphene.ID(required=True)

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


class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Decimal(required=True)
        description = graphene.String(required=True)
        # photo = Upload(required=True)  # Use Upload for file field
        category = graphene.String(required=False, default_value='General')

    product = graphene.Field(ProductType)

    def mutate(self, info, name, price, description, category):
        # Validate that price is non-negative
        if price < 0:
            raise GraphQLError('Price must be a non-negative value.')

        # Create and save the product
        product = Product(
            name=name,
            price=price,
            description=description,
            # photo=photo,
            category=category
        )
        product.save()

        return CreateProduct(product=product)


class Mutation(graphene.ObjectType):
    create_restaurant = CreateRestaurant.Field()
    create_product = CreateProduct.Field()