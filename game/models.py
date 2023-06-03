import uuid
import random
import string
from datetime import timedelta

from django.db import models
from django.utils import timezone

from game import buildings, exceptions
from utils.models import BaseModel


class GameSession(BaseModel):
    MINIMUM_PLAYERS = 2
    MAXIMUM_PLAYERS = 8
    GAME_CODE_LENGTH = 6
    DURATION = timedelta(hours=1)

    owner = models.OneToOneField("Player", on_delete=models.CASCADE, null=True, related_name="owned_game_session")
    game_code = models.CharField(max_length=GAME_CODE_LENGTH, null=False)
    has_started = models.BooleanField(default=False, null=False)
    ended_at = models.DateTimeField(null=True, default=None)

    def save(self, *args, **kwargs):
        if not self.game_code:
            self.generate_game_code()

        super().save(*args, **kwargs)

    def generate_game_code(self):
        self.game_code = "".join(random.choices(string.ascii_uppercase + string.digits, k=self.GAME_CODE_LENGTH))

    def __str__(self):
        return str(self.game_code)


class Player(BaseModel):
    NICKNAME_MIN_LENGTH = 3
    NICKNAME_MAX_LENGTH = 15

    nickname = models.CharField(max_length=NICKNAME_MAX_LENGTH, null=False)
    channel_name = models.UUIDField(default=uuid.uuid4, editable=False, null=False)
    is_connected = models.BooleanField(default=False, null=False)

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

    @property
    def town_hall(self):
        return buildings.TownHall(level=self.town_hall_level)

    @property
    def warehouse(self):
        return buildings.Warehouse(level=self.warehouse_level)

    @property
    def iron_mine(self):
        return buildings.IronMine(level=self.iron_mine_level)

    @property
    def clay_pit(self):
        return buildings.ClayPit(level=self.clay_pit_level)

    @property
    def sawmill(self):
        return buildings.Sawmill(level=self.sawmill_level)

    @property
    def barracks(self):
        return buildings.Barracks(level=self.barracks_level)

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

    def upgrade_building_level(self, name):
        if name == "town_hall":
            self.town_hall_level += 1
        elif name == "warehouse":
            self.warehouse_level += 1
        elif name == "iron_mine":
            self.iron_mine_level += 1
        elif name == "clay_pit":
            self.clay_pit_level += 1
        elif name == "sawmill":
            self.sawmill_level += 1
        elif name == "barracks":
            self.barracks_level += 1
        else:
            raise exceptions.BuildingNotFoundException

    def get_building(self, name):
        building = self.buildings.get(name, None)
        if not building:
            raise exceptions.BuildingNotFoundException

        return building

    def __str__(self):
        return f"Village {self.id}"
