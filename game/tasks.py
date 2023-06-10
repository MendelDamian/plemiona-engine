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


@app.task(bind=True)
def train_units_task(self, player_id, units_to_train: list[OrderedDict]):
    player = models.Player.objects.get(id=player_id)
    player.village.are_units_training = True
    player.village.save()

    current_task = models.Task.objects.create(game_session=player.game_session, task_id=self.request.id)

    for unit in units_to_train:
        unit_name, unit_count = unit["name"], unit["count"]

        unit_trainig_time = units.UNITS[unit_name].get_training_time(1).total_seconds()

        for _ in range(unit_count):
            sleep(unit_trainig_time)

            refreshed_player = models.Player.objects.get(id=player_id)
            refreshed_player.village.increase_unit_count(unit_name, 1)

            services.GameSessionConsumerService.send_fetch_units_count(refreshed_player)

    refreshed_player = models.Player.objects.get(id=player_id)
    refreshed_player.village.are_units_training = False
    refreshed_player.village.save()

    current_task.has_ended = True
    current_task.save()


@app.task(bind=True)
def attack_task(self, battle_id):
    battle = models.Battle.objects.get(id=battle_id)
    attack_time = battle.battle_time - battle.start_time

    current_task = models.Task.objects.create(game_session=battle.attacker.game_session, task_id=self.request.id)

    services.BattleService.attacker_preparations(battle)

    # TODO: send morale

    sleep(attack_time.total_seconds())

    winner = services.BattleService.battle_phase(models.Battle.objects.get(id=battle_id))

    if battle.attacker != winner:
        current_task.has_ended = True
        current_task.save()
        return

    sleep(attack_time.total_seconds() / 2)

    services.BattleService.attacker_return(models.Battle.objects.get(id=battle_id))

    current_task.has_ended = True
    current_task.save()
