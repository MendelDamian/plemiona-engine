from django.db import models

from utils.models import BaseModel


class Building(BaseModel):
    name = models.CharField(max_length=255, null=False)
    description = models.CharField(max_length=255, null=False)
    level = models.IntegerField(default=1, null=False)

    # Relations
    upgrades_from = models.OneToOneField(
        "self", on_delete=models.CASCADE, null=True, blank=True, default=None, related_name="upgrades_to"
    )

    # Resources
    wood_production = models.IntegerField(default=0, null=False, help_text="Per second")
    clay_production = models.IntegerField(default=0, null=False, help_text="Per second")
    iron_production = models.IntegerField(default=0, null=False, help_text="Per second")

    # Costs
    wood_cost = models.IntegerField(default=0, null=False)
    clay_cost = models.IntegerField(default=0, null=False)
    iron_cost = models.IntegerField(default=0, null=False)
    upgrade_time = models.IntegerField(default=0, null=False, help_text="In seconds")

    def __str__(self):
        return f"{self.name} {self.level}"

    def get_upgrade_cost(self):
        return {
            "wood": self.wood_cost,
            "clay": self.clay_cost,
            "iron": self.iron_cost,
        }


class TownHall(Building):
    wood_production = 0
    clay_production = 0
    iron_production = 0

    name = "Town Hall"
    description = "The Town Hall is the central building of your village. " \
                    "Upgrading it unlocks new buildings and upgrades."


class Granary(Building):
    pass


class IronMine(Building):
    pass


class ClayPit(Building):
    pass


class Sawmill(Building):
    pass


class Barracks(Building):
    pass
