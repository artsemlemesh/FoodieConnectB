from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status

from rest_framework.views import APIView
from .models import CartItem, Product, Order, OrderItem
from .serializers import CartItemSerializer, ProductSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from rest_framework import generics
import stripe
from django.conf import settings
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user)
            serializer = CartItemSerializer(cart_items, many=True, context={'request': request}) # explicitly pass context for displaying photos, in generics its send automatically
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
    

stripe.api_key = settings.STRIPE_SECRET_KEY

class CreatePaymentIntentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Amount is sent in cents
            amount = request.data.get('amount', 0)
            if amount <= 0:
                return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)

            # Create a Payment Intent
            payment_intent = stripe.PaymentIntent.create(
                amount=amount,  # Amount in cents
                currency='usd',
                payment_method_types=['card'],
            )

            return Response({'clientSecret': payment_intent['client_secret']}, status=status.HTTP_200_OK)

        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)





class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]