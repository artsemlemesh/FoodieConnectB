import graphene
from .types import OrderType
from cart.models import Order

class Query(graphene.ObjectType):
    all_orders = graphene.List(OrderType)

    def resolve_all_orders(root, info):
        return Order.objects.all()
