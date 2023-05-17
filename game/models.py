import random
import string

from django.db import models, IntegrityError
from django.db.models.signals import pre_save
from django.dispatch import receiver


class GameSession(models.Model):
    id = models.AutoField(primary_key=True)
    game_code = models.CharField(max_length=6, null=False)
    has_started = models.BooleanField(default=False, null=False)

    owner = models.ForeignKey("Player", on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = "Game session"
        verbose_name_plural = "Game sessions"

    def save(self, *args, **kwargs):
        if not self.game_code:
            self.generate_game_code()

        super().save(*args, **kwargs)

    def generate_game_code(self):
        self.game_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

    def __str__(self):
        return self.game_code


class Player(models.Model):
    id = models.AutoField(primary_key=True)
    nickname = models.CharField(max_length=30, null=False)

    game_session = models.ForeignKey("GameSession", on_delete=models.CASCADE, null=False)
    village = models.OneToOneField("Village", on_delete=models.CASCADE, null=False)

    class Meta:
        verbose_name = "Player"
        verbose_name_plural = "Players"

    def __str__(self):
        return self.nickname


class Village(models.Model):
    id = models.AutoField(primary_key=True)

    class Meta:
        verbose_name = "Village"
        verbose_name_plural = "Villages"
