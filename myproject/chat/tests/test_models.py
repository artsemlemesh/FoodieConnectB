import pytest
from django.contrib.auth import get_user_model
from chat.models import ChatRoom, Message

User = get_user_model()

@pytest.mark.django_db
def test_chat_room_creation():
    room = ChatRoom.objects.create(name="Test Room")
    assert ChatRoom.objects.count() == 1
    assert room.name == "Test Room"
    assert room.created_at is not None

@pytest.mark.django_db
def test_message_creation():
    user = User.objects.create_user(username="testuser", password="testpass")
    room = ChatRoom.objects.create(name="Test Room")
    message = Message.objects.create(user=user, room=room, content="Hello, world!")

    assert Message.objects.count() == 1
    assert message.user == user
    assert message.room == room
    assert message.content == "Hello, world!"
    assert message.timestamp is not None