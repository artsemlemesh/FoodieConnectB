import json
import pytest_asyncio
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from myproject.asgi import application  # Import your ASGI app

@pytest_asyncio.fixture
async def communicator():
    """
    Fixture to set up a WebSocket communicator.
    """
    communicator = WebsocketCommunicator(application, "/ws/chat/1/")
    connected, _ = await communicator.connect()
    assert connected
    yield communicator
    await communicator.disconnect()

async def test_receive_message(communicator):
    """
    Test that messages sent by the client are broadcast to the room group.
    """
    message_data = {"message": "Hello, world!"}

    # Send a message through the WebSocket
    await communicator.send_json_to(message_data)

    # Verify the WebSocket receives the message
    response = await communicator.receive_json_from()
    assert response["message"] == "Hello, world!"

async def test_broadcast_message(communicator):
    """
    Test that the consumer broadcasts messages to the WebSocket.
    """
    channel_layer = get_channel_layer()

    # Simulate sending a message to the group
    message_data = {"type": "chat_message", "message": "Broadcast test"}
    await channel_layer.group_send("chat_1", message_data)

    # Verify the WebSocket receives the message
    response = await communicator.receive_json_from()
    assert response["message"] == "Broadcast test"

async def test_disconnect(communicator):
    """
    Test that the WebSocket disconnects cleanly.
    """
    await communicator.disconnect()
    assert communicator.closed