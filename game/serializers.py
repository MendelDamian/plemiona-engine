from rest_framework import serializers

from game.buildings import Building
from game.models import Player, Village, GameSession


class CreateGameSessionSerializer(serializers.Serializer):
    nickname = serializers.CharField(
        max_length=Player.NICKNAME_MAX_LENGTH, min_length=Player.NICKNAME_MIN_LENGTH, required=True
    )
    game_code = serializers.CharField(max_length=GameSession.GAME_CODE_LENGTH, required=False, allow_blank=True)


class PlayerInLobbySerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ("id", "nickname")


class VillageCoordinatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Village
        fields = ("x", "y")


class PlayerDataSerializer(serializers.ModelSerializer):
    village = VillageCoordinatesSerializer()
    morale = serializers.SerializerMethodField()

    class Meta:
        model = Player
        fields = ("id", "morale", "nickname", "village")

    def get_morale(self, instance: Player):
        return instance.village.morale


class ResourcesSerializer(serializers.Serializer):
    resources = serializers.DictField()
    resourcesIncome = serializers.DictField()
    resourcesCapacity = serializers.IntegerField()

    def to_representation(self, instance: Village):
        return {
            "resources": instance.resources,
            "resourcesIncome": {
                "wood": instance.sawmill.get_production(),
                "clay": instance.clay_pit.get_production(),
                "iron": instance.iron_mine.get_production(),
            },
            "resourcesCapacity": instance.warehouse.get_capacity(),
        }


class BuldingSerializer(serializers.Serializer):
    level = serializers.IntegerField()
    max_level = serializers.IntegerField()
    upgrade_cost = serializers.DictField()
    upgrade_duration = serializers.IntegerField()

    def to_representation(self, instance: Building):
        return {
            "level": instance.level,
            "maxLevel": instance.MAX_LEVEL,
            "upgradeCost": instance.get_upgrade_cost(),
            "upgradeDuration": int(instance.get_upgrade_time().total_seconds()),
        }


class VillageSerializer(serializers.ModelSerializer):
    buildings = serializers.SerializerMethodField()

    class Meta:
        model = Village
        fields = ("buildings",)

    def get_buildings(self, instance: Village):
        return {
            "townHall": BuldingSerializer(instance.town_hall).data,
            "warehouse": BuldingSerializer(instance.warehouse).data,
            "sawmill": BuldingSerializer(instance.sawmill).data,
            "clayPit": BuldingSerializer(instance.clay_pit).data,
            "ironMine": BuldingSerializer(instance.iron_mine).data,
            "barracks": BuldingSerializer(instance.barracks).data,
        }


class PlayersLeaderboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ("id", "nickname", "points")
