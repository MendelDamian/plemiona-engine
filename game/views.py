from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.utils import timezone

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


class BattleListView(APIView):
    def get(self, request, *args, **kwargs):
        player = request.user

        battle_reports_qs = player.battles_as_attacker.all() | player.battles_as_defender.all()
        battle_reports = battle_reports_qs.filter(battle_time__lt=timezone.now()).order_by("-battle_time")[:5]

        battle_serializer = serializers.BattleSerializer(battle_reports, many=True).data

        return Response({"data": battle_serializer}, status=status.HTTP_200_OK)
