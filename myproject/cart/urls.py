from django.urls import path
from .views import CheckoutView, CartView, ProductListCreateView, ProductRetrieveUpdateDestroyView


app_name = 'cart'

urlpatterns = [
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('cart/', CartView.as_view(), name='cart'),

    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductRetrieveUpdateDestroyView.as_view(), name='product-retrieve-update-destroy'),

]