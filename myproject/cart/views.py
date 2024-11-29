from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status

from rest_framework.views import APIView
from .models import CartItem, Product, Order, OrderItem
from .serializers import CartItemSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user)
            serializer = CartItemSerializer(cart_items, many=True)
            return Response(serializer.data)
        else:
            return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    

    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user, product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return Response({'message': 'Item added to cart'}, status=status.HTTP_201_CREATED)
   
    def delete(self, request):
        product_id = request.data.get('product_id')
        cart_item = CartItem.objects.filter(user=request.user, product_id=product_id).first()
        if cart_item:
            cart_item.delete()
            return Response({'message': 'Item removed from cart'}, status=status.HTTP_200_OK)
        return Response({'error': 'Item not found in cart'}, status=status.HTTP_404_NOT_FOUND)
    
    def patch(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')

        if not quantity or int(quantity) < 1:
            return Response({'error': 'Quantity must be at least 1'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            cart_item = CartItem.objects.get(user=request.user, product_id=product_id)
        except CartItem.DoesNotExist:
            raise NotFound({'error': 'Cart item not found'})
        cart_item.quantity = quantity
        cart_item.save()
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class CheckoutView(APIView):
    def post(self, request):
        cart_items = CartItem.objects.filter(user=request.user)
        if not cart_items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        total_amount = sum(item.total_price() for item in cart_items)

        order = Order.objects.create(user=request.user, total_amount=total_amount)
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.total_price()
            )

        cart_items.delete() #clear the cart after order is created

        return Response({'message': 'Order Created successfully'}, status=status.HTTP_201_CREATED)