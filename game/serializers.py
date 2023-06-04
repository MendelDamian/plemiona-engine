from rest_framework import serializers

from game.models import Player, Village, GameSession


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ["id", "nickname"]


class VillageCoordinatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Village
        fields = ["x", "y"]


class PlayerStartGameSessionConsumerSerializer(serializers.ModelSerializer):
    village = VillageCoordinatesSerializer()

    class Meta:
        model = Player
        fields = ["id", "nickname", "village"]


class CreateGameSessionSerializer(serializers.Serializer):
    nickname = serializers.CharField(
        max_length=Player.NICKNAME_MAX_LENGTH, min_length=Player.NICKNAME_MIN_LENGTH, required=True
    )
    game_code = serializers.CharField(max_length=GameSession.GAME_CODE_LENGTH, required=False, allow_blank=True)


class BuildingSerializer(serializers.Serializer):
    level = serializers.IntegerField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["upgrade_cost"] = instance.get_upgrade_cost()
        data["upgrade_time"] = instance.get_upgrade_time().total_seconds()
        data["max_level"] = instance.MAX_LEVEL
        return data


class TownHallSerializer(BuildingSerializer):
    pass


class WarehouseSerializer(BuildingSerializer):
    capacity = serializers.SerializerMethodField()

    def get_capacity(self, instance):
        return instance.get_capacity()


class IronMineSerializer(BuildingSerializer):
    production = serializers.SerializerMethodField()

    def get_production(self, instance):
        return instance.get_production()


class ClayPitSerializer(BuildingSerializer):
    production = serializers.SerializerMethodField()

    def get_production(self, instance):
        return instance.get_production()


class SawmillSerializer(BuildingSerializer):
    production = serializers.SerializerMethodField()

    def get_production(self, instance):
        return instance.get_production()


class BarracksSerializer(BuildingSerializer):
    pass


class VillageSerializer(serializers.ModelSerializer):
    town_hall = TownHallSerializer()
    warehouse = WarehouseSerializer()
    iron_mine = IronMineSerializer()
    clay_pit = ClayPitSerializer()
    sawmill = SawmillSerializer()
    barracks = BarracksSerializer()

    class Meta:
        model = Village
        fields = (
            "morale",
            "town_hall",
            "warehouse",
            "iron_mine",
            "clay_pit",
            "sawmill",
            "barracks",
        )


class PlayerTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = [
            "id"
        ]
