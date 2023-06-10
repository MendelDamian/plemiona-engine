from rest_framework import serializers

from game.buildings import Building
from game.models import Player, Village, GameSession, Battle
from game.units import Unit


class CreateGameSessionSerializer(serializers.Serializer):
    nickname = serializers.CharField(
        max_length=Player.NICKNAME_MAX_LENGTH, min_length=Player.NICKNAME_MIN_LENGTH, required=True
    )
    game_code = serializers.CharField(max_length=GameSession.GAME_CODE_LENGTH, required=False, allow_blank=True)


class UnitsSerializer(serializers.Serializer):
    class UnitSerializer(serializers.Serializer):
        name = serializers.ChoiceField(
            choices=Village.UNIT_NAMES, required=True, error_messages={"invalid_choice": "Invalid unit name"}
        )
        count = serializers.IntegerField(min_value=1, required=True)

    units = UnitSerializer(many=True, required=True)


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
        village = self.context.get("village")
        if village:
            upgrade_duration = village.get_building_upgrade_time(instance)
        else:
            upgrade_duration = instance.BASE_UPGRADE_TIME

        return {
            "level": instance.level,
            "maxLevel": instance.MAX_LEVEL,
            "upgradeCost": instance.get_upgrade_cost(),
            "upgradeDuration": int(upgrade_duration),
        }


class VillageSerializer(serializers.ModelSerializer):
    buildings = serializers.SerializerMethodField()

    class Meta:
        model = Village
        fields = ("buildings",)

    def get_buildings(self, instance: Village):
        return {
            "townHall": BuldingSerializer(instance.town_hall, context={"village": instance}).data,
            "warehouse": BuldingSerializer(instance.warehouse, context={"village": instance}).data,
            "sawmill": BuldingSerializer(instance.sawmill, context={"village": instance}).data,
            "clayPit": BuldingSerializer(instance.clay_pit, context={"village": instance}).data,
            "ironMine": BuldingSerializer(instance.iron_mine, context={"village": instance}).data,
            "barracks": BuldingSerializer(instance.barracks, context={"village": instance}).data,
        }


class UnitsCountInVillageSerializer(serializers.Serializer):
    units = serializers.SerializerMethodField()

    def get_units(self, instance: Village):
        return {
            "spearman": {"count": instance.spearman_count},
            "swordsman": {"count": instance.swordsman_count},
            "axeman": {"count": instance.axeman_count},
            "archer": {"count": instance.archer_count},
        }


class UnitSerializer(serializers.Serializer):
    speed = serializers.IntegerField()
    trainig_duration = serializers.IntegerField()
    training_cost = serializers.DictField()
    carrying_capacity = serializers.IntegerField()
    offensive_strength = serializers.IntegerField()
    defensive_strength = serializers.IntegerField()
    count = serializers.IntegerField()

    def to_representation(self, instance: Unit):
        return {
            "count": instance.count,
            "speed": int(instance.SPEED.total_seconds()),
            "trainigDuration": int(instance.TRAINING_TIME.total_seconds()),
            "trainingCost": instance.get_training_cost(1),
            "carryingCapacity": instance.CARRYING_CAPACITY,
            "offensiveStrength": instance.OFFENSIVE_STRENGTH,
            "defensiveStrength": instance.DEFENSIVE_STRENGTH,
        }


class UnitsInVillageSerializer(serializers.Serializer):
    units = serializers.SerializerMethodField()

    def get_units(self, instance: Village):
        return {
            "spearman": UnitSerializer(instance.spearman).data,
            "swordsman": UnitSerializer(instance.swordsman).data,
            "axeman": UnitSerializer(instance.axeman).data,
            "archer": UnitSerializer(instance.archer).data,
        }


class PlayerResultsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ("id", "nickname", "points")


class BattleSerializer(serializers.ModelSerializer):
    attacker = PlayerDataSerializer()
    defender = PlayerDataSerializer()

    start_time = serializers.DateTimeField()
    battle_time = serializers.DateTimeField()
    return_time = serializers.DateTimeField()

    attacker_units = serializers.SerializerMethodField()
    defender_units = serializers.SerializerMethodField()

    left_attacker_units = serializers.SerializerMethodField()
    left_defender_units = serializers.SerializerMethodField()

    plundered_resources = serializers.DictField()

    class Meta:
        model = Battle
        fields = (
            "id",
            "attacker",
            "defender",
            "start_time",
            "battle_time",
            "return_time",
            "attacker_units",
            "defender_units",
            "left_attacker_units",
            "left_defender_units",
            "plundered_resources",
            "attacker_lost_morale",
            "defender_lost_morale",
        )

    def get_attacker_units(self, instance: Battle):
        return {unit_name: unit.count for unit_name, unit in instance.attacker_units.items()}

    def get_defender_units(self, instance: Battle):
        return {unit_name: unit.count for unit_name, unit in instance.defender_units.items()}

    def get_left_attacker_units(self, instance: Battle):
        return {unit_name: unit.count for unit_name, unit in instance.left_attacker_units.items()}

    def get_left_defender_units(self, instance: Battle):
        return {unit_name: unit.count for unit_name, unit in instance.left_defender_units.items()}
