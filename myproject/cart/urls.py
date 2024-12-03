from django.urls import path
from .views import CreatePaymentIntentView, CartView, ProductListCreateView, ProductRetrieveUpdateDestroyView


app_name = 'cart'

urlpatterns = [
    path('create-payment-intent/', CreatePaymentIntentView.as_view(), name='create-payment-intent'),
    path('cart/', CartView.as_view(), name='cart'),

    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductRetrieveUpdateDestroyView.as_view(), name='product-retrieve-update-destroy'),

]