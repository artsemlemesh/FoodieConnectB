from django.urls import path
from .views import CreatePaymentIntentView, CartView, ProductListCreateView, ProductRetrieveUpdateDestroyView, UpdateOrderStatusView, ConfirmPaymentView, OrderHistoryView

from webhooks.stripe_webhook import stripe_webhook

app_name = 'cart'

urlpatterns = [
    path('create-payment-intent/', CreatePaymentIntentView.as_view(), name='create-payment-intent'),
    path('cart/', CartView.as_view(), name='cart'),

    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductRetrieveUpdateDestroyView.as_view(), name='product-retrieve-update-destroy'),

    path('stripe/webhook/', stripe_webhook, name='stripe-webhook'),

    path('orders/<int:order_id>/update-status', UpdateOrderStatusView.as_view(), name='update-order-status'),
    path('payment/confirm/', ConfirmPaymentView.as_view(), name='confirm_payment'),

    path('orders/', OrderHistoryView.as_view(), name='order_history'),



]