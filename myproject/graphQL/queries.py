import graphene
from .types import OrderType, ReviewType
from cart.models import Order
from reviews.models import Review

class Query(graphene.ObjectType):
    all_orders = graphene.List(OrderType)
    pending_reviews = graphene.List(ReviewType)

    def resolve_all_orders(root, info):
        return Order.objects.all()
    
    def resolve_pending_reviews(self, info, **kwargs):
        return Review.objects.filter(is_approved=False)
