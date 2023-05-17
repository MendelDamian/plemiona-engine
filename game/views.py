from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from game.models import GameSession, Player, Village


class CreateGameSessionSerializer(serializers.Serializer):
    nickname = serializers.CharField(max_length=30, min_length=6, required=True)
    game_code = serializers.CharField(max_length=6, required=False, allow_blank=True)


class CreateJoinGameSessionView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = CreateGameSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        game_code = serializer.validated_data.pop("game_code", None)
        if game_code.strip() == "":
            game_code = None

        if game_code:
            try:
                game_session = GameSession.objects.get(game_code=game_code)
            except GameSession.DoesNotExist:
                return Response({"Game Session": ["Game session does not exist."]}, status=404)

            if game_session.has_started:
                return Response({"Game Session": ["Game has already started."]}, status=400)
        else:
            game_session = GameSession.objects.create(owner=None)

        player = Player(game_session=game_session, **serializer.validated_data)
        if Player.objects.filter(game_session=game_session, nickname=player.nickname).exists():
            return Response({"nickname": ["Nickname already in use."]}, status=400)
        player.village = Village.objects.create()
        player.save()

        if not game_session.owner:
            game_session.owner = player
            game_session.save()

        game_session.player_set.add(player)

        refresh = RefreshToken.for_user(player)
        response_data = {
            'token': str(refresh.access_token),
            'player_id': player.id,
            'game_session_id': game_session.id,
            "game_code": game_session.game_code,
        }
        return Response(response_data, status=201)
