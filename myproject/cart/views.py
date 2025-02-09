from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status

from rest_framework.views import APIView
from .models import CartItem, Product, Order, OrderItem
from .serializers import CartItemSerializer, ProductSerializer, OrderSerializer, OrderDeleteViewSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from rest_framework import generics
import stripe
from django.conf import settings
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .tasks import update_order_status
from django.views.generic import DeleteView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404
from myproject.utils import track_page_view
from django.core.cache import caches
from django.utils import timezone




class PageViewTrackingView(APIView):
    def post(self, request):
        page_url = request.data.get('page_url')
        if not page_url:
            return Response({'error': 'Page URL is required'}, status=status.HTTP_400_BAD_REQUEST)

        track_page_view(page_url, request.user.id if request.user.is_authenticated else None)
        return Response({'message': f'Page view for {page_url} tracked'}, status=status.HTTP_200_OK)

    def get(self, request):
        # Return page view count for a given page_url
        page_url = request.query_params.get('page_url')
        if not page_url:
            return Response({'error': 'Page URL is required'}, status=status.HTTP_400_BAD_REQUEST)

        cache = caches['page_view_cache']

        #total views
        total_views = cache.get(f'page_view:{page_url}', 0)
        #daily views
        daily_views_key = f'page_view_daily:{page_url}:{timezone.now().strftime("%Y-%m-%d")}'
        daily_views = cache.get(daily_views_key, 0)

        return Response({'page_url': page_url, 'total_views': total_views, 'daily_views': daily_views}, status=status.HTTP_200_OK)

        # page_view_count = cache.get(f'page_view:{page_url}', 0)
        # return Response({'page_url': page_url, 'page_view_count': page_view_count}, status=status.HTTP_200_OK)



class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        track_page_view('cart_page', request.user.id)

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
            order_id = request.data.get('order_id')


            if amount <= 0:
                return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)

            # Validate or retrieve existing order, prevents order duplicates
            if order_id:
                order = Order.objects.get(id=order_id, user=request.user)
            else:
                # Create a new order if no order_id is provided
                order = Order.objects.create(
                    user=request.user,
                    total_amount=amount / 100,
                    status='Pending'
                )


            # Create a Payment Intent
            payment_intent = stripe.PaymentIntent.create(
                amount=amount,  # Amount in cents
                currency='usd',
                payment_method_types=['card'],
                metadata={'order_id': order.id}  # Include order ID in metadata
            )


            return Response({
                'clientSecret': payment_intent['client_secret'],
                'order_id': order.id
            }, status=status.HTTP_200_OK)

        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ConfirmPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print('ConfirmPaymentView')
        order_id = request.data.get('order_id')

        try:
            # Retrieve the order using the order_id
            order = Order.objects.get(id=order_id, user=request.user)

            # Update the order status to 'Paid'
            order.status = 'Paid'
            order.save()

            update_order_status.delay(order.id)  # Call the Celery task asynchronously


            # Return a response with the success page URL
            return Response({'order_id': order.id}, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)   
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class UpdateOrderStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            new_status = request.data.get('status')

            if new_status not in [choice[0] for choice in Order.STATUS_CHOICES]:
                return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
            
            order.status = new_status
            order.save()


            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'order_{order_id}',
                {
                    'type': 'order_status_update',
                    'message': new_status
                }
            )

            return Response({'message': 'Order status updated successfully'}, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

class OrderDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            print(order.user)
            order_data = OrderDeleteViewSerializer(order).data
            print(order_data)
            order.delete()

            return Response(
                {"detail": "Order deleted successfully.", "order": order_data},
                status=status.HTTP_204_NO_CONTENT
            )
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)


class OrderHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        orders = Order.objects.filter(user=user).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=200)



