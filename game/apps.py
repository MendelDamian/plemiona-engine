import os

from django.apps import AppConfig


class GameConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "game"

    def ready(self):
        if os.environ.get("RUN_MAIN"):
            from game.models import Player

            Player.objects.update(is_connected=False)
