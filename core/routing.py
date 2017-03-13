from channels.routing import route, route_class

from .consumers import ws_connect, ws_disconnect, WsThread


channel_routing = [
    route('websocket.connect', ws_connect, path=r"^/ws/users/$"),
    route_class(WsThread, path=r"^/ws/thread/(?P<thread>\w+)$"),
    route('websocket.disconnect', ws_disconnect),
]
