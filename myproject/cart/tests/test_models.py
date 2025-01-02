import pytest
from chat.models import ChatRoom

@pytest.mark.django_db
def test_chatroom_creation():
    room = ChatRoom.objects.create(name="Test Room")
    assert room.name == "Test Room"