import random
import string
from datetime import timedelta

from django.db import models

from game import buildings
from utils.models import BaseModel


class GameSession(BaseModel):
    MINIMUM_PLAYERS = 2
    MAXIMUM_PLAYERS = 8
    DURATION = timedelta(hours=1)

    owner = models.ForeignKey("Player", on_delete=models.CASCADE, null=True)
    game_code = models.CharField(max_length=6, null=False)
    has_started = models.BooleanField(default=False, null=False)
    ended_at = models.DateTimeField(null=True, default=None)

    def save(self, *args, **kwargs):
        if not self.game_code:
            self.generate_game_code()

        super().save(*args, **kwargs)

    def generate_game_code(self):
        self.game_code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

    def __str__(self):
        return self.game_code


class Player(BaseModel):
    NICKNAME_MIN_LENGTH = 3
    NICKNAME_MAX_LENGTH = 15

    nickname = models.CharField(max_length=15, null=False)
    game_session = models.ForeignKey("GameSession", on_delete=models.CASCADE, null=False)
    village = models.OneToOneField("Village", on_delete=models.CASCADE, null=False)

    is_authenticated = True

    class Meta:
        unique_together = ("game_session", "nickname")

    def save(self, *args, **kwargs):
        # Check if the player has a village, avoid RelatedObjectDoesNotExist
        if not hasattr(self, "village"):
            self.village = Village.objects.create()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.nickname


class Village(BaseModel):
    morale = models.IntegerField(default=100, null=False)

    # Resoources
    wood = models.IntegerField(default=0, null=False)
    iron = models.IntegerField(default=0, null=False)
    clay = models.IntegerField(default=0, null=False)

    @property
    def resources(self):
        return {"wood": self.wood, "iron": self.iron, "clay": self.clay}

    # Level of the buildings
    town_hall_level = models.IntegerField(default=1, null=False)
    granary_level = models.IntegerField(default=1, null=False)
    iron_mine_level = models.IntegerField(default=1, null=False)
    clay_pit_level = models.IntegerField(default=1, null=False)
    sawmill_level = models.IntegerField(default=1, null=False)
    barracks_level = models.IntegerField(default=1, null=False)

    @property
    def town_hall(self):
        return buildings.TownHall(level=self.town_hall_level)

    @property
    def granary(self):
        return buildings.Granary(level=self.granary_level)

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

    def __str__(self):
        return f"Village {self.id}"
