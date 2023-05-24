import random
import string

from django.db import models

from utils.models import BaseModel


class GameSession(BaseModel):
    MINIMUM_PLAYERS = 2
    MAXIMUM_PLAYERS = 8

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
    wood = models.IntegerField(default=0, null=False)
    iron = models.IntegerField(default=0, null=False)
    clay = models.IntegerField(default=0, null=False)
    morale = models.IntegerField(default=100, null=False)

    # Buildings
    town_hall = models.ForeignKey("building.TownHall", on_delete=models.SET_NULL, null=True, default=None)
    granary = models.ForeignKey("building.Granary", on_delete=models.SET_NULL, null=True, default=None)
    iron_mine = models.ForeignKey("building.IronMine", on_delete=models.SET_NULL, null=True, default=None)
    clay_pit = models.ForeignKey("building.ClayPit", on_delete=models.SET_NULL, null=True, default=None)
    sawmill = models.ForeignKey("building.Sawmill", on_delete=models.SET_NULL, null=True, default=None)
    barracks = models.ForeignKey("building.Barracks", on_delete=models.SET_NULL, null=True, default=None)

    def __str__(self):
        return f"Village {self.id}"

    def get_resources(self):
        return {
            "wood": self.wood,
            "iron": self.iron,
            "clay": self.clay,
        }
