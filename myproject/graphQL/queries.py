import graphene
from .types import OrderType, ReviewType, ProductType, ProductFilterInput, ProductConnection, PageInfo
from cart.models import Order, Product
from reviews.models import Review
from graphene import relay
import base64


class Query(graphene.ObjectType):
    all_orders = graphene.List(OrderType) #fetch all orders
    pending_reviews = graphene.List(ReviewType) #fetch pending reviews
    # all_products = relay.ConnectionField(
    #         ProductConnection,
    #         filter=ProductFilterInput(),
    # )
    all_products = relay.ConnectionField(ProductConnection, first=graphene.Int(), after=graphene.String(), filter=ProductFilterInput()) #fetch all products with pagination and filtering
    all_categories = graphene.List(graphene.String)  # Query for categories

    def resolve_all_categories(self, info):
        return Product.objects.values_list("category", flat=True).distinct() #fetches all unique categories from the database, to avoid duplicates that are being created with each new product

    def resolve_all_orders(root, info): #fetches all orders from the database
        return Order.objects.all()
    
    def resolve_pending_reviews(self, info, **kwargs): #fetches all pending reviews from the database
        return Review.objects.filter(is_approved=False)



    def resolve_all_products(self, info, first=None, after=None, filter=None):
        qs = Product.objects.all() #fetch all products from the database

        if filter and filter.get('category'): #filter products by category if filter is applied
            qs = qs.filter(category__icontains=filter['category']) #returns products with category that contains the filter value

        if after: #fetch products after the cursor
            try:
                # Decode the cursor
                cursor = base64.b64decode(after).decode('utf-8')
                after_id = cursor.split(':')[-1]  # Assuming cursor is formatted as "arrayconnection:{id}"
                qs = qs.filter(id__gt=after_id)  # Fetch products with IDs greater than the after_id
            except (ValueError, IndexError):
                raise Exception("Invalid cursor")

        # Limit the queryset based on the 'first' argument
        if first:
            qs = qs[:first]

        # Create edges
        edges = [ 
            ProductConnection.Edge(node=product, cursor=base64.b64encode(f"arrayconnection:{product.id}".encode()).decode())
            for product in qs
        ]

        # Determine if there are more products
        has_next_page = len(edges) == (first if first else 0)
        #the cursor of the last item in the list
        end_cursor = edges[-1].cursor if edges else None

        # Return a ProductConnection object with the edges and page info
        return ProductConnection(edges=edges, page_info=PageInfo(has_next_page=has_next_page, end_cursor=end_cursor))
