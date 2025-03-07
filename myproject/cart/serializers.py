from rest_framework import serializers
from .models import CartItem, Product, OrderItem, Order
from django.contrib.auth import get_user_model
from users.serializers import UserSerializer

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


# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = get_user_model()
#         fields = ['id', 'username', 'email'] 

class OrderDeleteViewSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Order
        fields = ['id', 'user', 'created_at', 'total_amount', 'status', 'eta', 'restaurant']  # Add or remove fields as necessary


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    user = UserSerializer()

    class Meta:
        model = Order
        fields = ['id', 'user', 'created_at', 'status', 'total_amount', 'eta', 'items']


