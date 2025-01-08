import graphene
from .types import OrderType, ReviewType, ProductType
from cart.models import Order, Product
from reviews.models import Review

class Query(graphene.ObjectType):
    all_orders = graphene.List(OrderType)
    pending_reviews = graphene.List(ReviewType)
    all_products = graphene.List(ProductType)

    def resolve_all_orders(root, info):
        return Order.objects.all()
    
    def resolve_pending_reviews(self, info, **kwargs):
        return Review.objects.filter(is_approved=False)

    def resolve_all_products(root, info):
        return Product.objects.all()
