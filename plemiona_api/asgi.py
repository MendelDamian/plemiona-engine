"""
ASGI config for plemiona_api project.
"""

import os

from django.core.asgi import get_asgi_application

django_asgi_app = get_asgi_application()
from channels.routing import ProtocolTypeRouter, URLRouter

from utils.jwt_authentication import JwtAuthMiddlewareStack
from game.routing import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plemiona_api.settings")


application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": JwtAuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
    }
)
