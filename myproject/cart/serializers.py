from rest_framework import serializers
from .models import CartItem, Product, OrderItem, Order


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'description', 'photo', 'category']


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    # product_name = serializers.ReadOnlyField(source='product.name')
    # product_photo = serializers.ImageField(source='product.photo')
    total_price = serializers.SerializerMethodField()


    class Meta:
        model = CartItem
        fields = ['id', 'product',  'quantity', 'total_price']
    
    
    def get_total_price(self, obj):
        return obj.quantity * obj.product.price
    


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'created_at', 'status', 'total_amount', 'eta', 'items']


