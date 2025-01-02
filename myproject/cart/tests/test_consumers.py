# import pytest
# from channels.testing import WebsocketCommunicator
# from channels.layers import get_channel_layer
# from django.contrib.auth import get_user_model
# from cart.models import Order
# from cart.consumers import OrderConsumer
# from asgiref.sync import async_to_sync
# import json
# from django.test import TestCase



# class TestOrderConsumer(TestCase):
#     async def test_connect_and_receive_initial_state(self, settings):
#         # Set up
#         settings.CHANNEL_LAYERS = {
#             "default": {
#                 "BACKEND": "channels.layers.InMemoryChannelLayer",
#             },
#         }

#         order = Order.objects.create(
#             user=get_user_model().objects.create_user(username="testuser"),
#             total_amount=100.0,
#             status="Pending",
#         )
#         communicator = WebsocketCommunicator(
#             OrderConsumer.as_asgi(), f"/ws/orders/{order.id}/"
#         )

#         # Connect
#         connected, subprotocol = await communicator.connect()
#         assert connected, "WebSocket connection failed."

#         # Verify group join
#         channel_layer = get_channel_layer()
#         assert channel_layer

#         # Verify initial order state is sent
#         response = await communicator.receive_json_from()
#         assert response["status"] == "Pending"
#         assert response["eta"] is None
#         assert response["position"] == {"lat": 40.712776, "lng": -74.005974}

#         # Disconnect
#         await communicator.disconnect()

#     async def test_order_status_update(self, settings):
#         # Set up
#         settings.CHANNEL_LAYERS = {
#             "default": {
#                 "BACKEND": "channels.layers.InMemoryChannelLayer",
#             },
#         }

#         order = Order.objects.create(
#             user=get_user_model().objects.create_user(username="testuser"),
#             total_amount=100.0,
#             status="Pending",
#         )
#         communicator = WebsocketCommunicator(
#             OrderConsumer.as_asgi(), f"/ws/orders/{order.id}/"
#         )
#         connected, subprotocol = await communicator.connect()
#         assert connected, "WebSocket connection failed."

#         # Simulate a status update
#         channel_layer = get_channel_layer()
#         new_status = "Delivered"
#         new_eta = "2024-12-31T15:00:00"
#         new_position = {"lat": 40.73061, "lng": -73.935242}

#         async_to_sync(channel_layer.group_send)(
#             f"order_{order.id}",
#             {
#                 "type": "order_status_update",
#                 "status": new_status,
#                 "eta": new_eta,
#                 "position": new_position,
#             },
#         )

#         # Verify the message was received
#         response = await communicator.receive_json_from()
#         assert response["status"] == new_status
#         assert response["eta"] == new_eta
#         assert response["position"] == new_position

#         # Disconnect
#         await communicator.disconnect()

#     async def test_invalid_order_id(self, settings):
#         # Set up
#         settings.CHANNEL_LAYERS = {
#             "default": {
#                 "BACKEND": "channels.layers.InMemoryChannelLayer",
#             },
#         }

#         invalid_order_id = 9999
#         communicator = WebsocketCommunicator(
#             OrderConsumer.as_asgi(), f"/ws/orders/{invalid_order_id}/"
#         )
#         connected, subprotocol = await communicator.connect()
#         assert connected, "WebSocket connection failed."

#         # Verify disconnection when order is invalid
#         try:
#             await communicator.receive_json_from()
#         except Exception as e:
#             assert str(e) == "Order matching query does not exist."

#         await communicator.disconnect()

#     async def test_disconnect(self, settings):
#         # Set up
#         settings.CHANNEL_LAYERS = {
#             "default": {
#                 "BACKEND": "channels.layers.InMemoryChannelLayer",
#             },
#         }

#         order = Order.objects.create(
#             user=get_user_model().objects.create_user(username="testuser"),
#             total_amount=100.0,
#             status="Pending",
#         )
#         communicator = WebsocketCommunicator(
#             OrderConsumer.as_asgi(), f"/ws/orders/{order.id}/"
#         )
#         connected, subprotocol = await communicator.connect()
#         assert connected, "WebSocket connection failed."

#         # Verify disconnection
#         await communicator.disconnect()
#         assert True, "WebSocket disconnected successfully."