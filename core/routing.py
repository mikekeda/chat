from django.core.asgi import get_asgi_application
from django.urls import re_path

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack

from core.consumers import WsUsers, WsThread


chat = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(
                    [
                        re_path(r"^ws/users/$", WsUsers.as_asgi()),
                        re_path(r"^ws/thread/(?P<thread>\w+)$", WsThread.as_asgi()),
                    ]
                )
            )
        ),
    }
)
