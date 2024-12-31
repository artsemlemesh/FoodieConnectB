from django.urls import re_path
from cart.consumers import OrderConsumer
from chat.consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r'ws/orders/(?P<order_id>\d+)/$', OrderConsumer.as_asgi()),

    re_path(r'ws/chat/(?P<room_id>\d+)/$', ChatConsumer.as_asgi()),

]