from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import publicchat.routing
import privatechat.routing

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            [
                *publicchat.routing.websocket_urlpatterns,
                *privatechat.routing.websocket_urlpatterns,
            ]
        )
    ),
})