from time import sleep
from collections import OrderedDict

from game import exceptions, models, services
from plemiona_api.celery import app


@app.task(bind=True)
def upgrade_building_task(self, player_id, building_name, seconds):
    from game.services import GameSessionConsumerService

    if building_name not in models.Village.BUILDING_NAMES:
        raise exceptions.BuildingNotFoundException

    player = models.Player.objects.get(id=player_id)
    player.village.set_building_upgrading_state(building_name, True)

    current_task = models.Task.objects.create(game_session=player.game_session, task_id=self.request.id)

    sleep(seconds)

    refreshed_player = models.Player.objects.get(id=player_id)
    refreshed_player.village.update_resources()

    refreshed_player.village.upgrade_building_level(building_name)
    refreshed_player.village.set_building_upgrading_state(building_name, False)

    GameSessionConsumerService.send_fetch_buildings(refreshed_player)
    GameSessionConsumerService.send_fetch_resources(refreshed_player)

    current_task.has_ended = True


@app.task
def send_leaderboard_task(game_session_id, seconds):
    sleep(seconds)

    game_session = models.GameSession.objects.get(id=game_session_id)
    services.GameSessionService.end_game_session(game_session)


@app.task(bind=True)
def train_units_task(self, player_id, units_to_train: list[OrderedDict]):
    from game.units import UNITS
    from game.services import GameSessionConsumerService

    player = models.Player.objects.get(id=player_id)
    player.village.are_units_training = True
    player.village.save()

    current_task = models.Task.objects.create(game_session=player.game_session, task_id=self.request.id)

    for unit in units_to_train:
        unit_name, unit_count = unit["name"], unit["count"]

        unit_trainig_time = UNITS[unit_name].get_training_time(1).total_seconds()

        for _ in range(unit_count):
            sleep(unit_trainig_time)

            refreshed_player = models.Player.objects.get(id=player_id)
            refreshed_player.village.increase_unit_count(unit_name, 1)

            GameSessionConsumerService.send_fetch_units_count(refreshed_player)

    refreshed_player = models.Player.objects.get(id=player_id)
    refreshed_player.village.are_units_training = False
    refreshed_player.village.save()

    current_task.has_ended = True
