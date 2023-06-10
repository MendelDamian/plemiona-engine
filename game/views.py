from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.db.models import Q

from game import serializers, services, models


class CreateJoinGameSessionView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = serializers.CreateGameSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        nickname = serializer.validated_data["nickname"]
        game_code = serializer.validated_data.pop("game_code", None)

        game_session = services.GameSessionService.get_or_create_game_session(game_code)
        player = services.GameSessionService.join_game_session(game_session, nickname)

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
        services.GameSessionService.start_game_session(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UpgradeBuildingView(APIView):
    def post(self, request, building_name, *args, **kwargs):
        services.VillageService.upgrade_building(request.user, building_name)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TrainUnitsView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = serializers.UnitsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        units_to_train = serializer.validated_data["units"]
        services.VillageService.train_units(request.user, units_to_train=units_to_train)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AttackPlayerView(APIView):
    def post(self, request, defender_id, *args, **kwargs):
        serializer = serializers.UnitsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        defender = get_object_or_404(models.Player, id=defender_id)
        attacker_units = serializer.validated_data["units"]

        services.VillageService.attack_player(request.user, defender, attacker_units)

        return Response(status=status.HTTP_204_NO_CONTENT)


class BattleListView(ListAPIView):
    serializer_class = serializers.BattleSerializer

    def get_queryset(self):
        player = self.request.user
        return player.battles_as_attacker.all() | player.battles_as_defender.all()
