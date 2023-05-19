from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from game.models import GameSession, Player


class CreateGameSessionSerializer(serializers.Serializer):
    nickname = serializers.CharField(
        max_length=Player.NICKNAME_MAX_LENGTH, min_length=Player.NICKNAME_MIN_LENGTH, required=True
    )
    game_code = serializers.CharField(max_length=6, required=False, allow_blank=True)


class CreateJoinGameSessionView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = CreateGameSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        error = {
            "errors": {}
        }

        nickname = serializer.validated_data["nickname"]
        game_code = serializer.validated_data.pop("game_code", None)
        if game_code and game_code.strip() == "":
            game_code = None

        if game_code:
            try:
                game_session = GameSession.objects.get(game_code=game_code)
            except GameSession.DoesNotExist:
                error["errors"]["Game session"] = ["does not exist."]
                return Response(error, status=status.HTTP_404_NOT_FOUND)

            if game_session.has_started:
                error["errors"]["Game session"] = ["has already started."]
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
        else:
            game_session = GameSession.objects.create(owner=None)

        if Player.objects.filter(game_session=game_session, nickname=nickname).exists():
            error["errors"]["Nickname"] = ["is already in use."]
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        player = Player.objects.create(game_session=game_session, nickname=nickname)

        if not game_session.owner:
            game_session.owner = player
            game_session.save()

        game_session.player_set.add(player)

        refresh = RefreshToken.for_user(player)
        response_data = {
            "token": str(refresh.access_token),
            "player_id": player.id,
            "game_session_id": game_session.id,
            "game_code": game_session.game_code,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


class StartGameSessionView(APIView):
    def post(self, request, *args, **kwargs):
        error = {
            "errors": {}
        }

        player = request.user
        if player != player.game_session.owner:
            error["errors"]["Player"] = ["is not the owner."]
            return Response(error, status=status.HTTP_403_FORBIDDEN)

        if player.game_session.has_started:
            error["errors"]["Game session"] = ["has already started."]
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        if player.game_session.player_set.count() < 2:
            error["errors"]["Game session"] = ["requires minimum 2 players to start the game."]
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        player.game_session.has_started = True
        player.game_session.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
