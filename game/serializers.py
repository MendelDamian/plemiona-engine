from rest_framework import serializers

from game.models import Player


class PlayerInListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ["id", "nickname"]


class PlayerInGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ["id", "nickname", "resources", "town_hall", "granary", "iron_mine", "clay_pit", "sawmill", "barracks"]


class CreateGameSessionSerializer(serializers.Serializer):
    nickname = serializers.CharField(
        max_length=Player.NICKNAME_MAX_LENGTH, min_length=Player.NICKNAME_MIN_LENGTH, required=True
    )
    game_code = serializers.CharField(max_length=6, required=False, allow_blank=True)


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


class GranarySerializer(BuildingSerializer):
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


class VillageSerializer(serializers.Serializer):
    morale = serializers.IntegerField()
    town_hall = TownHallSerializer()
    granary = GranarySerializer()
    iron_mine = IronMineSerializer()
    clay_pit = ClayPitSerializer()
    sawmill = SawmillSerializer()
    barracks = BarracksSerializer()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["resources"] = instance.resources
        return data
