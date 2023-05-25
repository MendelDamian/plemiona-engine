"""
ASGI config for plemiona_api project.
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

from .management import JwtAuthMiddlewareStack
import game.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plemiona_api.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JwtAuthMiddlewareStack(
        URLRouter(
            game.routing.websocket_urlpatterns
        )
    )
})
