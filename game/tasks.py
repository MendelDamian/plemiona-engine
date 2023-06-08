from time import sleep
from collections import OrderedDict

from game import exceptions
from game.models import Player, Village, GameSession
from plemiona_api.celery import app


@app.task
def upgrade_building_task(player_id, building_name, seconds):
    from game.services import GameSessionConsumerService

    if building_name not in Village.BUILDING_NAMES:
        raise exceptions.BuildingNotFoundException

    player = Player.objects.get(id=player_id)
    player.village.set_building_upgrading_state(building_name, True)
    player.village.save()

    sleep(seconds)

    refreshed_player = Player.objects.get(id=player_id)
    refreshed_player.village.update_resources()

    refreshed_player.village.upgrade_building_level(building_name)
    refreshed_player.village.set_building_upgrading_state(building_name, False)
    refreshed_player.village.save()

    GameSessionConsumerService.send_fetch_buildings(refreshed_player)
    GameSessionConsumerService.send_fetch_resources(refreshed_player)


@app.task
def send_leaderboard_task(game_session_id, seconds):
    from game.services import GameSessionConsumerService

    sleep(seconds)

    game_session = GameSession.objects.get(id=game_session_id)
    GameSessionConsumerService.send_fetch_leaderboard(game_session)


@app.task
def train_units_task(player_id, units_to_train: list[OrderedDict]):
    from game.units import UNITS
    from game.services import GameSessionConsumerService

    player = Player.objects.get(id=player_id)
    player.village.are_units_training = True
    player.village.save()

    for unit in units_to_train:
        unit_name, unit_count = unit["name"], unit["count"]

        unit_trainig_time = UNITS[unit_name].get_training_time(1).total_seconds()

        for _ in range(unit_count):
            sleep(unit_trainig_time)

            refreshed_player = Player.objects.get(id=player_id)
            refreshed_player.village.increase_unit_count(unit_name, 1)

            GameSessionConsumerService.send_fetch_units_count(refreshed_player)

    refreshed_player = Player.objects.get(id=player_id)
    refreshed_player.village.are_units_training = False
    refreshed_player.village.save()
