from time import sleep

from game import models, services
from plemiona_api.celery import app


@app.task
def upgrade_building_task(player_id, building_name):
    player = models.Player.objects.get(id=player_id)

    player.village.upgrade_building_level(building_name)
    player.village.set_building_upgrading_state(building_name, False)

    services.GameSessionConsumerService.send_fetch_buildings(player)
    services.GameSessionConsumerService.send_fetch_resources(player)
    services.GameSessionConsumerService.inform_player(player, f"Building {building_name} has been upgraded")


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
