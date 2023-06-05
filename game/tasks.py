from time import sleep

from celery import shared_task

from game.models import Player


@shared_task
def upgrade_building_task(player_id, building_name, seconds):
    from game.services import GameSessionConsumerService

    sleep(seconds)

    player = Player.objects.get(id=player_id)
    village = player.village
    building = village.get_building(building_name)

    building.upgrade()
    village.upgrade_building_level(building_name)
    village.save()

    GameSessionConsumerService.send_fetch_buildings(player)
