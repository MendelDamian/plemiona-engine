from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from game.serializers import CreateGameSessionSerializer
from game.services import GameSessionService, VillageService


class CreateJoinGameSessionView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = CreateGameSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        nickname = serializer.validated_data["nickname"]
        game_code = serializer.validated_data.pop("game_code", None)

        game_session = GameSessionService.get_or_create_game_session(game_code)
        player = GameSessionService.join_game_session(game_session, nickname)

        refresh = RefreshToken.for_user(player)
        response_data = {
            "token": str(refresh.access_token),
            "player_id": player.id,
            "game_session_id": game_session.id,
            "nickname": player.nickname,
            "owner_id": game_session.owner.id,
            "game_code": game_session.game_code,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


class StartGameSessionView(APIView):
    def post(self, request, *args, **kwargs):
        GameSessionService.start_game_session(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UpgradeBuildingView(APIView):
    def post(self, request, building_name, *args, **kwargs):
        VillageService.upgrade_building(request.user, building_name)
        return Response(status=status.HTTP_204_NO_CONTENT)
