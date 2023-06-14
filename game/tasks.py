from time import sleep
from collections import OrderedDict

from game import exceptions, models, services, units
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
    current_task.save()


@app.task
def end_game_task(game_session_id, seconds):
    sleep(seconds)

    game_session = models.GameSession.objects.get(id=game_session_id)
    services.GameSessionService.end_game_session(game_session)


@app.task
def train_unit_task(player_id, unit_name):
    player = models.Player.objects.get(id=player_id)
    player.village.increase_unit_count(unit_name, 1)
    services.GameSessionConsumerService.send_fetch_units_count(player)


@app.task
def attack_task(battle_id):
    battle = models.Battle.objects.get(id=battle_id)
    services.BattleService.battle_phase(battle)


@app.task
def return_units_task(battle_id):
    services.BattleService.attacker_return(models.Battle.objects.get(id=battle_id))


@app.task
def send_delayed_message_task(player_id, message: str):
    services.GameSessionConsumerService.inform_player(models.Player.objects.get(id=player_id), message)
