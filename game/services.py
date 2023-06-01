from django.utils import timezone

from game import exceptions
from game.models import GameSession, Player


class GameSessionService:
    @staticmethod
    def get_or_create_game_session(game_code=None):
        if game_code:
            try:
                game_session = GameSession.objects.get(game_code=game_code)
            except GameSession.DoesNotExist:
                raise exceptions.GameSessionNotFoundException

            if game_session.has_started:
                raise exceptions.GameSessionAlreadyStartedException

            if game_session.player_set.count() >= GameSession.MAXIMUM_PLAYERS:
                raise exceptions.GameSessionFullException
        else:
            game_session = GameSession.objects.create(owner=None)

        return game_session

    @staticmethod
    def join_game_session(game_session, nickname):
        if Player.objects.filter(game_session=game_session, nickname=nickname).exists():
            raise exceptions.NicknameAlreadyInUseException

        player = Player.objects.create(game_session=game_session, nickname=nickname)
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

        if game_session.player_set.count() < GameSession.MINIMUM_PLAYERS:
            raise exceptions.MinimumPlayersNotReachedException

        game_session.has_started = True
        game_session.ended_at = timezone.now() + GameSession.DURATION
        game_session.save()


class VillageService:
    @staticmethod
    def upgrade_building(player, building_name):
        village = player.village
        building = village.get_building(building_name)
        upgrade_costs = building.get_upgrade_cost()
        village_resources = village.resources

        for resource in upgrade_costs:
            if village_resources[resource] < upgrade_costs[resource]:
                raise exceptions.InsufficientResourcesException

        for resource in upgrade_costs:
            village_resources[resource] -= upgrade_costs[resource]

        building.upgrade()
        village.upgrade_building_level(building_name)
        village.save()
