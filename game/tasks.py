from celery import shared_task
from time import sleep
from game.models import Player


@shared_task
def task(player_data, seconds):
    from game.services import GameSessionConsumerService
    sleep(seconds)
    player = Player.objects.get(id=player_data["id"])
    GameSessionConsumerService.send_fetch_resources(player)
    GameSessionConsumerService.send_fetch_buildings(player)
