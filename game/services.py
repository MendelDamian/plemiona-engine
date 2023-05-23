from game.models import GameSession, Player
from game import exceptions


class GameSessionService:
    @staticmethod
    def create_game_session(game_code=None):
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
        if player != player.game_session.owner:
            raise exceptions.NotOwnerException

        if player.game_session.has_started:
            raise exceptions.GameSessionAlreadyStartedException

        if player.game_session.player_set.count() < GameSession.MINIMUM_PLAYERS:
            raise exceptions.MinimumPlayersNotReachedException

        player.game_session.has_started = True
        player.game_session.save()
