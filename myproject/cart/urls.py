from django.urls import path
from .views import CheckoutView, CartView


app_name = 'cart'

urlpatterns = [
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('cart/', CartView.as_view(), name='cart'),

]