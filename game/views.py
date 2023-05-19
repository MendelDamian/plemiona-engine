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

        nickname = serializer.validated_data["nickname"]
        game_code = serializer.validated_data.pop("game_code", None)
        if game_code and game_code.strip() == "":
            game_code = None

        if game_code:
            try:
                game_session = GameSession.objects.get(game_code=game_code)
            except GameSession.DoesNotExist:
                return Response({"Game Session": ["does not exist."]}, status=status.HTTP_404_NOT_FOUND)

            if game_session.has_started:
                return Response({"Game Session": ["has already started."]}, status=status.HTTP_400_BAD_REQUEST)
        else:
            game_session = GameSession.objects.create(owner=None)

        if Player.objects.filter(game_session=game_session, nickname=nickname).exists():
            return Response({"Nickname": ["is already in use."]}, status=status.HTTP_400_BAD_REQUEST)
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
        player = request.user
        if player != player.game_session.owner:
            return Response({"Player": ["is not the owner."]}, status=status.HTTP_403_FORBIDDEN)

        if player.game_session.has_started:
            return Response({"Game session": ["has already started."]}, status=400)

        if player.game_session.player_set.count() < 2:
            return Response({"Game session": ["requires minimum 2 players to start the game."]}, status=400)

        player.game_session.has_started = True
        player.game_session.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
