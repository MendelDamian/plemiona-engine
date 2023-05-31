from channels.layers import get_channel_layer
from django.utils import timezone

from game import exceptions
from game.models import GameSession, Player
from game.consumers import GameConsumer


class GameSessionConsumerService:
    @staticmethod
    def send_players_list(game_session):
        game_consumer = GameConsumer()
        game_consumer.room_group_name = game_session.game_code
        game_consumer.channel_layer = get_channel_layer()
        game_consumer.send_players_list(game_session)

    @staticmethod
    def send_start_game_session(game_session):
        game_consumer = GameConsumer()
        game_consumer.room_group_name = game_session.game_code
        game_consumer.channel_layer = get_channel_layer()
        game_consumer.send_start_game_session()

    @staticmethod
    def send_village_data(player):
        game_consumer = GameConsumer()
        game_consumer.room_group_name = player.game_session.game_code
        game_consumer.channel_layer = get_channel_layer()
        game_consumer.village_data(player.village)


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

        GameSessionConsumerService.send_start_game_session(game_session)
        GameSessionConsumerService.send_village_data(player)
