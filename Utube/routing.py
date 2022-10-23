from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import chat.routing
import privatechat.routing

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            [
                *chat.routing.websocket_urlpatterns,
                *privatechat.routing.websocket_urlpatterns,
            ]
        )
    ),
})