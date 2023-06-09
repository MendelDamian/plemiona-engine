import random
from typing import OrderedDict

from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from plemiona_api.celery import app

from game import exceptions, serializers, models, tasks, units, buildings


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

        game_session_duration = game_session.DURATION.total_seconds()
        tasks.end_game_task.delay(game_session.id, game_session_duration)

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
        upgrade_costs = building.get_upgrade_cost()
        village.charge_resources(upgrade_costs)

        upgrade_time = village.get_building_upgrade_time(building)
        tasks.upgrade_building_task.delay(player.id, building_name, upgrade_time)
        GameSessionConsumerService.send_fetch_resources(player)

    @staticmethod
    def train_units(player, units_to_train: list[OrderedDict]):
        if not player.game_session.has_started:
            raise exceptions.GameSessionNotStartedException

        if player.game_session.has_ended:
            raise exceptions.GameSessionAlreadyEndedException

        if player.village.are_units_training:
            raise exceptions.UnitsAreAlreadyBeingTrainedException

        accumulated_cost = {"wood": 0, "clay": 0, "iron": 0}

        for unit in units_to_train:
            unit_name, unit_count = unit["name"], unit["count"]

            trainig_cost = units.UNITS[unit_name].get_training_cost(unit_count)

            for resource_name, resource_cost in trainig_cost.items():
                accumulated_cost[resource_name] += resource_cost

        village = player.village
        village.update_resources()
        village.charge_resources(accumulated_cost)

        tasks.train_units_task.delay(player.id, units_to_train)
        GameSessionConsumerService.send_fetch_resources(player)


class CoordinateService:
    AVAILABLE_TILES = (
        (0, 0),
        (0, 1),
        (0, 2),
        (0, 3),
        (0, 4),
        (0, 5),
        (0, 6),
        (0, 7),
        # TODO: Fill rest when map will be ready
    )

    @staticmethod
    def set_coordinates(game_session):
        left_coordinates = set(CoordinateService.AVAILABLE_TILES)

        for player in game_session.player_set.all():
            village = player.village
            village.x, village.y = random.choice(tuple(left_coordinates))
            left_coordinates.remove((village.x, village.y))
            village.save()
