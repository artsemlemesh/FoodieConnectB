from rest_framework import serializers
from .models import CartItem, Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'description', 'photo']

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