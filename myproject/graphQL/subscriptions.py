# # from graphene_subscriptions.signals import post_save_subscription
# from chat.models import Message
# import graphene
# # from graphene_subscriptions.events import CREATED
# from .types import MessageType


# # Automatically trigger subscription events on Message creation
# # post_save_subscription.connect(sender=Message)
# #REPLACE graphene_subscriptions WITH MORE COMPATIBLE

# class Subscription(graphene.ObjectType):
#     message_added = graphene.Field(MessageType, room_id=graphene.ID())

#     def resolve_message_added(self, info, room_id):
#         return None  # Subscription listens to events and doesn't need initial data