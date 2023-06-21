import random
from math import sqrt, pow
from typing import OrderedDict

from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from plemiona_api.celery import app

from game import exceptions, serializers, models, tasks, units


class GameSessionConsumerService:
    @staticmethod
    def send_start_game_session(game_session: models.GameSession):
        data = {
            "type": "start_game_session",
            "data": {
                "players": serializers.PlayerDataSerializer(game_session.player_set.all(), many=True).data,
                "endedAt": game_session.ended_at.isoformat(),
            },
        }
        GameSessionConsumerService._send_message(game_session.game_code, data)

    @staticmethod
    def send_fetch_resources(player: models.Player):
        data = {
            "type": "fetch_resources",
            "data": serializers.ResourcesSerializer(player.village).data,
        }
        GameSessionConsumerService._send_message(player.channel_name, data)

    @staticmethod
    def send_fetch_buildings(player: models.Player):
        data = {
            "type": "fetch_buildings",
            "data": serializers.VillageSerializer(player.village).data,
        }
        GameSessionConsumerService._send_message(player.channel_name, data)

    @staticmethod
    def send_fetch_units_count(player: models.Player):
        data = {
            "type": "fetch_units",
            "data": serializers.UnitsCountInVillageSerializer(player.village).data,
        }
        GameSessionConsumerService._send_message(player.channel_name, data)

    @staticmethod
    def send_fetch_units(player: models.Player):
        data = {
            "type": "fetch_units",
            "data": serializers.UnitsInVillageSerializer(player.village).data,
        }
        GameSessionConsumerService._send_message(player.channel_name, data)

    @staticmethod
    def send_fetch_leaderboard(game_session: models.GameSession):
        player_results_list = serializers.PlayerResultsSerializer(game_session.player_set.all(), many=True).data
        data = {
            "type": "fetch_leaderboard",
            "data": {
                "leaderboard": sorted(player_results_list, key=lambda x: x["points"], reverse=True),
            },
        }
        GameSessionConsumerService._send_message(game_session.game_code, data)

    @staticmethod
    def send_morale(player: models.Player):
        data = {
            "type": "morale_change",
            "data": {
                "morale": player.village.morale,
            },
        }
        GameSessionConsumerService._send_message(player.channel_name, data)

    @staticmethod
    def send_battle_log(game_session: models.GameSession):
        battles = game_session.battles.order_by("-start_time")[:10]

        data = {
            "type": "battle_log",
            "data": {
                "battleLog": serializers.BattleLogSerializer(battles, many=True).data,
            },
        }
        GameSessionConsumerService._send_message(game_session.game_code, data)

    @staticmethod
    def inform_player(player: models.Player, message: str):
        data = {
            "type": "message",
            "data": {
                "message": message,
            },
        }
        GameSessionConsumerService._send_message(player.channel_name, data)

    @staticmethod
    def _send_message(channel_name, data):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            str(channel_name),
            {
                "type": "send_message",
                "data": data,
            },
        )


class GameSessionService:
    @staticmethod
    def get_or_create_game_session(game_code=None):
        if game_code:
            try:
                game_session = models.GameSession.objects.get(game_code=game_code)
            except models.GameSession.DoesNotExist:
                raise exceptions.GameSessionNotFoundException

            if game_session.has_started:
                raise exceptions.GameSessionAlreadyStartedException

            if game_session.player_set.count() >= models.GameSession.MAXIMUM_PLAYERS:
                raise exceptions.GameSessionFullException
        else:
            game_session = models.GameSession.objects.create(owner=None)

        return game_session

    @staticmethod
    def join_game_session(game_session, nickname):
        if models.Player.objects.filter(game_session=game_session, nickname=nickname).exists():
            raise exceptions.NicknameAlreadyInUseException

        player = models.Player.objects.create(game_session=game_session, nickname=nickname)
        if not game_session.owner:
            game_session.owner = player
            game_session.save()

        game_session.player_set.add(player)

        return player

    @staticmethod
    def start_game_session(player):
        game_session = player.game_session
        if player != game_session.owner:
            raise exceptions.NotOwnerException

        if game_session.has_started:
            raise exceptions.GameSessionAlreadyStartedException

        if game_session.player_set.count() < models.GameSession.MINIMUM_PLAYERS:
            raise exceptions.MinimumPlayersNotReachedException

        game_session.has_started = True
        game_session.ended_at = timezone.now() + models.GameSession.DURATION
        game_session.save()

        # Start gathering resources for all players
        village_queryset = models.Village.objects.filter(player__game_session=game_session)
        village_queryset.update(last_resources_update=timezone.now())

        CoordinateService.set_coordinates(game_session)
        GameSessionConsumerService.send_start_game_session(game_session)
        for player in game_session.player_set.all():
            GameSessionConsumerService.send_fetch_resources(player)
            GameSessionConsumerService.send_fetch_buildings(player)
            GameSessionConsumerService.send_fetch_units(player)

        tasks.end_game_task.apply_async((game_session.id,), eta=game_session.ended_at)

    @staticmethod
    def end_game_session(game_session):
        for task in game_session.task_set.all():
            if not task.has_ended:
                app.control.revoke(task.task_id, terminate=True)
                task.has_ended = True

        GameSessionConsumerService.send_fetch_leaderboard(game_session)


class VillageService:
    @staticmethod
    def upgrade_building(player, building_name):
        if building_name not in models.Village.BUILDING_NAMES:
            raise exceptions.BuildingNotFoundException

        if not player.game_session.has_started:
            raise exceptions.GameSessionNotStartedException

        if player.game_session.has_ended:
            raise exceptions.GameSessionAlreadyEndedException

        village = player.village
        village.update_resources()

        if village.buildings_upgrading_state[building_name]:
            raise exceptions.BuildingUpgradeException

        building = village.buildings[building_name]
        building.validate_upgrade()

        upgrade_costs = building.get_upgrade_cost()
        village.charge_resources(upgrade_costs)
        village.set_building_upgrading_state(building_name, False)
        GameSessionConsumerService.send_fetch_resources(player)

        upgrade_time = village.get_building_upgrade_time(building)
        tasks.upgrade_building_task.apply_async((player.id, building_name), countdown=upgrade_time)

    @staticmethod
    def train_units(player, units_to_train: list[OrderedDict]):
        if not player.game_session.has_started:
            raise exceptions.GameSessionNotStartedException

        if player.game_session.has_ended:
            raise exceptions.GameSessionAlreadyEndedException

        if player.village.are_units_training:
            raise exceptions.UnitsAreAlreadyBeingTrainedException

        accumulated_cost = {"wood": 0, "clay": 0, "iron": 0}
        units_count = 0

        for unit in units_to_train:
            unit_name, unit_count = unit["name"], unit["count"]
            training_cost = units.UNITS[unit_name].get_training_cost(unit_count)
            units_count += unit_count

            for resource_name, resource_cost in training_cost.items():
                accumulated_cost[resource_name] += resource_cost

        if units_count == 0:
            raise exceptions.NoUnitsToTrainException

        village = player.village
        village.update_resources()
        village.charge_resources(accumulated_cost)
        GameSessionConsumerService.send_fetch_resources(player)

        finish_training_time = timezone.now()

        for unit in units_to_train:
            unit_name, unit_count = unit["name"], unit["count"]
            training_time = units.UNITS[unit_name].get_training_time(1)

            for _ in range(unit_count):
                finish_training_time += training_time
                tasks.train_unit_task.apply_async((player.id, unit_name), eta=finish_training_time)

        tasks.send_delayed_message_task.apply_async(
            (player.id, "Units are ready to be picked up!"), eta=finish_training_time
        )

    @staticmethod
    def attack_player(attacker: models.Player, defender: models.Player, attacker_units: list[OrderedDict]):
        if attacker == defender:
            raise exceptions.CannotAttackYourselfException

        slowest_unit = None
        attacker_units_dict = {}

        for unit in attacker_units:
            unit_name, unit_count = unit["name"], unit["count"]
            if unit_count <= 0:
                continue

            attacker_units_dict[unit_name] = unit_count
            current_unit = attacker.village.units[unit_name]

            if current_unit.count < unit_count:
                raise exceptions.InsufficientUnitsException

            if not slowest_unit or current_unit.SPEED > slowest_unit.SPEED:
                slowest_unit = current_unit

        if not slowest_unit:
            raise exceptions.NoUnitsToAttackException

        distance = sqrt(
            pow(attacker.village.x - defender.village.x, 2) + pow(attacker.village.y - defender.village.y, 2)
        )

        attack_time = slowest_unit.get_speed(distance)
        battle = models.Battle.objects.create(
            game_session=attacker.game_session,
            attacker=attacker,
            defender=defender,
            battle_time=timezone.now() + attack_time,
            attacker_spearman_count=attacker_units_dict.get("spearman", 0),
            attacker_swordsman_count=attacker_units_dict.get("swordsman", 0),
            attacker_axeman_count=attacker_units_dict.get("axeman", 0),
            attacker_archer_count=attacker_units_dict.get("archer", 0),
        )

        BattleService.send_units(battle)


class BattleService:
    @staticmethod
    def send_units(battle: models.Battle):
        battle.attacker.village.spearman_count -= battle.attacker_spearman_count
        battle.attacker.village.swordsman_count -= battle.attacker_swordsman_count
        battle.attacker.village.axeman_count -= battle.attacker_axeman_count
        battle.attacker.village.archer_count -= battle.attacker_archer_count

        battle.attacker.village.save()
        GameSessionConsumerService.send_fetch_units_count(battle.attacker)
        GameSessionConsumerService.inform_player(battle.defender, f"{battle.attacker.nickname}'s units are incoming!")
        GameSessionConsumerService.send_battle_log(battle.attacker.game_session)

        tasks.attack_task.apply_async((battle.id,), eta=battle.battle_time)

    @staticmethod
    def battle_phase(battle: models.Battle):
        attacker = battle.attacker
        defender = battle.defender
        defender.village.update_resources()

        battle.defender_spearman_count = defender.village.units["spearman"].count
        battle.defender_swordsman_count = defender.village.units["swordsman"].count
        battle.defender_axeman_count = defender.village.units["axeman"].count
        battle.defender_archer_count = defender.village.units["archer"].count

        battle.defender_strenght = 1 + sum([unit.defensive_strength for unit in defender.village.units.values()])
        battle.defender_strenght *= models.Village.DEFENSIVE_BONUS
        battle.attacker_strenght = sum([unit.offensive_strength for unit in battle.attacker_units.values()])

        ratio = min(battle.attacker_strenght, battle.defender_strenght) / max(
            battle.attacker_strenght, battle.defender_strenght
        )

        winner = attacker if battle.attacker_strenght > battle.defender_strenght else defender
        if winner == attacker:
            battle.left_attacker_spearman_count = round(battle.attacker_spearman_count * (1 - ratio))
            battle.left_attacker_swordsman_count = round(battle.attacker_swordsman_count * (1 - ratio))
            battle.left_attacker_axeman_count = round(battle.attacker_axeman_count * (1 - ratio))
            battle.left_attacker_archer_count = round(battle.attacker_archer_count * (1 - ratio))

            battle.attacker_lost_morale = models.Battle.BASE_MORALE_LOSS * ratio * 0.5
            battle.defender_lost_morale = models.Battle.BASE_MORALE_LOSS * (1 - ratio)

            attacker_capacity = sum([unit.get_carrying_capacity for unit in battle.left_attacker_units.values()])

            battle.plundered_wood = min(defender.village.wood, attacker_capacity)
            battle.plundered_clay = min(defender.village.clay, attacker_capacity)
            battle.plundered_iron = min(defender.village.iron, attacker_capacity)

            defender.village.charge_resources(battle.plundered_resources)

            defender.village.morale -= battle.defender_lost_morale
            attack_time = battle.battle_time - battle.start_time
            battle.return_time = timezone.now() + attack_time / 2

            GameSessionConsumerService.inform_player(
                defender, f"You have lost the defense against {attacker.nickname}!"
            )
        else:
            battle.left_defender_spearman_count = round(battle.defender_spearman_count * (1 - ratio))
            battle.left_defender_swordsman_count = round(battle.defender_swordsman_count * (1 - ratio))
            battle.left_defender_axeman_count = round(battle.defender_axeman_count * (1 - ratio))
            battle.left_defender_archer_count = round(battle.defender_archer_count * (1 - ratio))

            battle.attacker_lost_morale = models.Battle.BASE_MORALE_LOSS * (1 - ratio)

            GameSessionConsumerService.inform_player(attacker, f"{defender.nickname} has defended himself!")
            GameSessionConsumerService.inform_player(
                defender, f"You have successfully defended yourself from {attacker.nickname}!"
            )

        battle.save()

        defender.village.spearman_count = battle.left_defender_spearman_count
        defender.village.swordsman_count = battle.left_defender_swordsman_count
        defender.village.axeman_count = battle.left_defender_axeman_count
        defender.village.archer_count = battle.left_defender_archer_count
        defender.village.save()

        GameSessionConsumerService.send_fetch_units_count(defender)
        GameSessionConsumerService.send_fetch_resources(defender)
        GameSessionConsumerService.send_morale(defender)

        if winner == attacker:
            tasks.return_units_task.apply_async((battle.id,), eta=battle.return_time)
            GameSessionConsumerService.send_battle_log(battle.attacker.game_session)

    @staticmethod
    def attacker_return(battle: models.Battle):
        battle.attacker.village.spearman_count += battle.left_attacker_spearman_count
        battle.attacker.village.swordsman_count += battle.left_attacker_swordsman_count
        battle.attacker.village.axeman_count += battle.left_attacker_axeman_count
        battle.attacker.village.archer_count += battle.left_attacker_archer_count
        battle.attacker.village.morale -= battle.attacker_lost_morale
        battle.attacker.village.save()

        battle.attacker.village.add_resources(battle.plundered_resources)
        battle.attacker.village.update_resources()

        GameSessionConsumerService.inform_player(battle.attacker, "Your units returned from battle!")
        GameSessionConsumerService.send_fetch_units_count(battle.attacker)
        GameSessionConsumerService.send_fetch_resources(battle.attacker)
        GameSessionConsumerService.send_morale(battle.attacker)


class CoordinateService:
    AVAILABLE_TILES = (
        (3, 5),
        (3, 11),
        (9, 8),
        (13, 9),
        (11, 14),
        (19, 9),
        (17, 3),
        (9, 2),
    )

    @staticmethod
    def set_coordinates(game_session):
        left_coordinates = set(CoordinateService.AVAILABLE_TILES)

        for player in game_session.player_set.all():
            village = player.village
            village.x, village.y = random.choice(tuple(left_coordinates))
            left_coordinates.remove((village.x, village.y))
            village.save()
