from ariadne import QueryType, MutationType, SubscriptionType, make_executable_schema
from ariadne.asgi import GraphQL
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
import asyncio

# Define type definitions
type_defs = """
type User {
    id: ID!
    username: String!
    email: String!
}

type ChatRoom {
    id: ID!
    name: String!
    createdAt: String!
    messages: [Message!]
}

type Message {
    id: ID!
    user: User!
    content: String!
    timestamp: String!
}

type Query {
    chatRooms: [ChatRoom!]!
    messages(roomId: ID!): [Message!]!
}

type Mutation {
    createChatRoom(name: String!): ChatRoom!
    createMessage(roomId: ID!, content: String!): Message!
}

type Subscription {
    messageAdded(roomId: ID!): Message!
}
"""

# Query resolvers
query = QueryType()

@query.field("chatRooms")
def resolve_chat_rooms(_, info):
    from chat.models import ChatRoom
    return ChatRoom.objects.all()

@query.field("messages")
def resolve_messages(_, info, roomId):
    from chat.models import  Message

    return Message.objects.filter(room_id=roomId).order_by("timestamp")

# Mutation resolvers
mutation = MutationType()

@mutation.field("createChatRoom")
def resolve_create_chat_room(_, info, name):
    from chat.models import ChatRoom
    room = ChatRoom.objects.create(name=name)
    return room

@mutation.field("createMessage")
def resolve_create_message(_, info, roomId, content):
    user = info.context["request"].user
    if not user.is_authenticated:
        raise Exception("Authentication required.")

    try:
        from chat.models import ChatRoom
        room = ChatRoom.objects.get(id=roomId)
    except ChatRoom.DoesNotExist:
        raise Exception("Chat room does not exist.")
    
    from chat.models import Message
    message = Message.objects.create(user=user, room=room, content=content)

    # Broadcast the message via WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"room_{roomId}",
        {"type": "message_added", "message": message},
    )

    return message

# Subscription resolvers
subscription = SubscriptionType()

@subscription.source("messageAdded")
async def message_added_generator(_, info, roomId):
    channel_layer = get_channel_layer()
    group_name = f"room_{roomId}"

    # Add the user to the group
    async_to_sync(channel_layer.group_add)(group_name, info.context["channel_name"])

    # Simulate listening for new messages
    while True:
        await asyncio.sleep(1)

@subscription.field("messageAdded")
def resolve_message_added(message, info):
    return message

# Create executable schema
schema = make_executable_schema(type_defs, query, mutation, subscription)