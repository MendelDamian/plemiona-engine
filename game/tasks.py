from time import sleep

from game import exceptions, models
from plemiona_api.celery import app


@app.task
def upgrade_building_task(player_id, building_name, seconds):
    from game.services import GameSessionConsumerService

    if building_name not in models.Village.BUILDING_NAMES:
        raise exceptions.BuildingNotFoundException

    player = models.Player.objects.get(id=player_id)
    player.village.set_building_upgrading_state(building_name, True)
    player.village.save()

    sleep(seconds)

    refreshed_player = models.Player.objects.get(id=player_id)
    refreshed_player.village.update_resources()

    refreshed_player.village.upgrade_building_level(building_name)
    refreshed_player.village.set_building_upgrading_state(building_name, False)
    refreshed_player.village.save()

    GameSessionConsumerService.send_fetch_buildings(refreshed_player)
    GameSessionConsumerService.send_fetch_resources(refreshed_player)
