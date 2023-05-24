import random
import string

from django.db import models


class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


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
    pass
