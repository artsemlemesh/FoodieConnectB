


from django.urls import path
from .views import start_delivery, get_orders

app_name = 'livedel'

urlpatterns = [
    path('orders/<int:order_id>/start-delivery/', start_delivery, name='start_delivery'),
    path('orders/<int:order_id>/', get_orders, name='get_orders'),
]