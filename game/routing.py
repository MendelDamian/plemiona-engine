from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/lobby-socket/", consumers.LobbyConsumer.as_asgi())
]
