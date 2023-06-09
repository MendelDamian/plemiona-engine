import uuid
import random
import string
from datetime import timedelta

from django.db import models
from django.utils import timezone

from game import exceptions, units
from game.buildings import Building, TownHall, Warehouse, IronMine, ClayPit, Sawmill, Barracks
from utils.models import BaseModel


class GameSession(BaseModel):
    MINIMUM_PLAYERS = 2
    MAXIMUM_PLAYERS = 8
    GAME_CODE_LENGTH = 6
    DURATION = timedelta(hours=1)

    owner = models.OneToOneField("Player", on_delete=models.CASCADE, null=True, related_name="owned_game_session")
    game_code = models.CharField(max_length=GAME_CODE_LENGTH, null=False, unique=True, editable=False, db_index=True)
    has_started = models.BooleanField(default=False, null=False)
    ended_at = models.DateTimeField(null=True, default=None)

    @property
    def has_ended(self):
        return timezone.now() >= self.ended_at

    def save(self, *args, **kwargs):
        if not self.game_code:
            self.generate_game_code()

        super().save(*args, **kwargs)

    def generate_game_code(self):
        self.game_code = "".join(random.choices(string.ascii_uppercase + string.digits, k=self.GAME_CODE_LENGTH))

    def __str__(self):
        return str(self.game_code)


class Task(BaseModel):
    TASK_ID_LENGTH = 36

    task_id = models.CharField(max_length=TASK_ID_LENGTH, null=False)
    has_ended = models.BooleanField(default=False, null=False)

    game_session = models.ForeignKey("GameSession", on_delete=models.CASCADE, null=False)

    def __str__(self):
        return str(self.task_id)


class Player(BaseModel):
    NICKNAME_MIN_LENGTH = 3
    NICKNAME_MAX_LENGTH = 15

    nickname = models.CharField(max_length=NICKNAME_MAX_LENGTH, null=False)
    channel_name = models.UUIDField(default=uuid.uuid4, editable=False, null=False)

    game_session = models.ForeignKey("GameSession", on_delete=models.CASCADE, null=False)
    village = models.OneToOneField("Village", on_delete=models.CASCADE, null=False)

    is_authenticated = True

    class Meta:
        unique_together = ("game_session", "nickname")

    @property
    def points(self):
        return sum([building.points for _, building in self.village.buildings.items()])

    def save(self, *args, **kwargs):
        # Check if the player has a village, avoid RelatedObjectDoesNotExist
        if not hasattr(self, "village"):
            self.village = Village.objects.create()

        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.nickname)


class Village(BaseModel):
    MAX_MORALE = 100
    BUILDING_NAMES = ("town_hall", "warehouse", "iron_mine", "clay_pit", "sawmill", "barracks")
    UNIT_NAMES = ("spearman", "swordsman", "axeman", "archer")

    morale = models.IntegerField(default=MAX_MORALE, null=False)

    # Coordinates
    x = models.IntegerField(default=0, null=False)
    y = models.IntegerField(default=0, null=False)

    # Resoources
    wood = models.FloatField(default=150, null=False)
    iron = models.FloatField(default=150, null=False)
    clay = models.FloatField(default=150, null=False)

    last_resources_update = models.DateTimeField(null=True, default=None)

    @property
    def resources(self):
        return {"wood": round(self.wood), "iron": round(self.iron), "clay": round(self.clay)}

    # Level of the buildings
    town_hall_level = models.IntegerField(default=1, null=False)
    warehouse_level = models.IntegerField(default=1, null=False)
    iron_mine_level = models.IntegerField(default=1, null=False)
    clay_pit_level = models.IntegerField(default=1, null=False)
    sawmill_level = models.IntegerField(default=1, null=False)
    barracks_level = models.IntegerField(default=1, null=False)

    # Upgrading status
    is_town_hall_upgrading = models.BooleanField(default=False, null=False)
    is_warehouse_upgrading = models.BooleanField(default=False, null=False)
    is_iron_mine_upgrading = models.BooleanField(default=False, null=False)
    is_clay_pit_upgrading = models.BooleanField(default=False, null=False)
    is_sawmill_upgrading = models.BooleanField(default=False, null=False)
    is_barracks_upgrading = models.BooleanField(default=False, null=False)

    # Units in the barracks
    spearman_count = models.IntegerField(default=0, null=False)
    swordsman_count = models.IntegerField(default=0, null=False)
    axeman_count = models.IntegerField(default=0, null=False)
    archer_count = models.IntegerField(default=0, null=False)

    are_units_training = models.BooleanField(default=False, null=False)

    @property
    def spearman(self):
        return units.Spearman(count=self.spearman_count)

    @property
    def swordsman(self):
        return units.Swordsman(count=self.swordsman_count)

    @property
    def axeman(self):
        return units.Axeman(count=self.axeman_count)

    @property
    def archer(self):
        return units.Archer(count=self.archer_count)

    @property
    def units(self) -> dict[str, units.Unit]:
        return {
            "spearman": self.spearman,
            "swordman": self.swordsman,
            "axeman": self.axeman,
            "archer": self.archer,
        }

    @property
    def town_hall(self):
        return TownHall(level=self.town_hall_level)

    @property
    def warehouse(self):
        return Warehouse(level=self.warehouse_level)

    @property
    def iron_mine(self):
        return IronMine(level=self.iron_mine_level)

    @property
    def clay_pit(self):
        return ClayPit(level=self.clay_pit_level)

    @property
    def sawmill(self):
        return Sawmill(level=self.sawmill_level)

    @property
    def barracks(self):
        return Barracks(level=self.barracks_level)

    @property
    def buildings(self):
        return {
            "town_hall": self.town_hall,
            "warehouse": self.warehouse,
            "iron_mine": self.iron_mine,
            "clay_pit": self.clay_pit,
            "sawmill": self.sawmill,
            "barracks": self.barracks,
        }

    @property
    def buildings_upgrading_state(self):
        return {
            "town_hall": self.is_town_hall_upgrading,
            "warehouse": self.is_warehouse_upgrading,
            "iron_mine": self.is_iron_mine_upgrading,
            "clay_pit": self.is_clay_pit_upgrading,
            "sawmill": self.is_sawmill_upgrading,
            "barracks": self.is_barracks_upgrading,
        }

    def update_resources(self):
        if not self.last_resources_update:
            self.last_resources_update = timezone.now()
            self.save()
            return

        seconds_passed = (timezone.now() - self.last_resources_update).total_seconds()

        self.wood += self.sawmill.get_production(seconds_passed)
        self.iron += self.iron_mine.get_production(seconds_passed)
        self.clay += self.clay_pit.get_production(seconds_passed)

        warehouse_capacity = self.warehouse.get_capacity()
        self.wood = min(self.wood, warehouse_capacity)
        self.iron = min(self.iron, warehouse_capacity)
        self.clay = min(self.clay, warehouse_capacity)

        self.last_resources_update = timezone.now()
        self.save()

    def charge_resources(self, resources):
        if self.wood < resources["wood"] or self.iron < resources["iron"] or self.clay < resources["clay"]:
            raise exceptions.InsufficientResourcesException

        self.wood -= resources["wood"]
        self.iron -= resources["iron"]
        self.clay -= resources["clay"]

        self.save()

    def upgrade_building_level(self, building_name):
        if building_name == "town_hall":
            self.town_hall_level += 1
        elif building_name == "warehouse":
            self.warehouse_level += 1
        elif building_name == "iron_mine":
            self.iron_mine_level += 1
        elif building_name == "clay_pit":
            self.clay_pit_level += 1
        elif building_name == "sawmill":
            self.sawmill_level += 1
        elif building_name == "barracks":
            self.barracks_level += 1
        else:
            raise exceptions.BuildingNotFoundException

        self.save()

    def set_building_upgrading_state(self, building_name, state):
        if building_name == "town_hall":
            self.is_town_hall_upgrading = state
        elif building_name == "warehouse":
            self.is_warehouse_upgrading = state
        elif building_name == "iron_mine":
            self.is_iron_mine_upgrading = state
        elif building_name == "clay_pit":
            self.is_clay_pit_upgrading = state
        elif building_name == "sawmill":
            self.is_sawmill_upgrading = state
        elif building_name == "barracks":
            self.is_barracks_upgrading = state
        else:
            raise exceptions.BuildingNotFoundException

        self.save()

    def increase_unit_count(self, unit_name, count):
        if unit_name == "spearman":
            self.spearman_count += count
        elif unit_name == "swordman":
            self.swordsman_count += count
        elif unit_name == "axeman":
            self.axeman_count += count
        elif unit_name == "archer":
            self.archer_count += count
        else:
            raise exceptions.UnitNotFoundException

        self.save()

    def get_building_upgrade_time(self, building: Building):
        town_hall = self.town_hall
        return (
            building.BASE_UPGRADE_TIME
            * (building.UPGRADE_TIME_FACTOR**building.level)
            * (town_hall.UPGRADE_TIME_DISCOUNT ** (-town_hall.level))
        ).total_seconds()

    def __str__(self):
        return f"Village {self.id}"
