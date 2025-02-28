


from django.urls import path
from .views import get_order, move_delivery

app_name = 'livedel'

urlpatterns = [
    path('orders/<int:order_id>/', get_order, name='get_order'),
    path('orders/<int:order_id>/move/', move_delivery, name='move_delivery'),
]