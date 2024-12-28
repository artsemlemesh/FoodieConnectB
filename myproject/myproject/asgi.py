import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from .routing import websocket_urlpatterns
from chat.schema import schema  # Ariadne schema
from ariadne.asgi import GraphQL
from django.urls import path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")

def get_graphql_application():
    from chat.schema import schema  # Import schema only when needed
    return GraphQL(schema, debug=True)


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            *websocket_urlpatterns,
            path("graphql/", get_graphql_application()),  # Use function to return GraphQL ASGI app

        ])
    ),
})