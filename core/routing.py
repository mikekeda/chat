from django.conf.urls import url
from django.core.asgi import get_asgi_application

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from core.consumers import WsUsers, WsThread


chat = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(
                [
                    url(r"^ws/users/$", WsUsers.as_asgi()),
                    url(r"^ws/thread/(?P<thread>\w+)$", WsThread.as_asgi()),
                ]
            )
        ),
    }
)
