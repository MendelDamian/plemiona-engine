from datetime import timedelta
from typing import ClassVar

from game import exceptions


class Building:
    MAX_LEVEL: ClassVar[int] = 1
    BASE_UPGRADE_TIME: ClassVar[timedelta] = timedelta(minutes=1)

    # Multiplier
    COST_MULTIPLIER: ClassVar[float] = 0

    # Upgrade costs
    BASE_WOOD_COST: ClassVar[int] = 0
    BASE_CLAY_COST: ClassVar[int] = 0
    BASE_IRON_COST: ClassVar[int] = 0

    def __init__(self, level: int = 1) -> None:
        self.level = level

    def get_upgrade_cost(self) -> dict:
        return {
            "wood": self.BASE_WOOD_COST * self.level,
            "clay": self.BASE_CLAY_COST * self.level,
            "iron": self.BASE_IRON_COST * self.level,
        }

    def get_upgrade_time(self) -> timedelta:
        return self.BASE_UPGRADE_TIME * self.level

    def upgrade(self) -> None:
        if self.level < self.MAX_LEVEL:
            self.level += 1
        else:
            raise exceptions.BuildingMaxLevelException

    def downgrade(self) -> None:
        if self.level > 1:
            self.level -= 1


class ResourceBuilding(Building):
    # Multiplier
    PRODUCTION_MULTIPLIER: ClassVar[float] = 0

    # Producation per second
    BASE_WOOD_PRODUCTION: ClassVar[float] = 0
    BASE_CLAY_PRODUCTION: ClassVar[float] = 0
    BASE_IRON_PRODUCTION: ClassVar[float] = 0

    def get_production(self) -> dict:
        return {
            "wood": self.BASE_WOOD_PRODUCTION * self.level,
            "clay": self.BASE_CLAY_PRODUCTION * self.level,
            "iron": self.BASE_IRON_PRODUCTION * self.level,
        }


class TownHall(Building):
    MAX_LEVEL = 3
    BASE_UPGRADE_TIME = timedelta(minutes=10)

    # Costs
    BASE_WOOD_COST = 200
    BASE_CLAY_COST = 170
    BASE_IRON_COST = 90


class Granary(Building):
    MAX_LEVEL = 15
    BASE_UPGRADE_TIME = timedelta(minutes=3)

    # Costs
    BASE_WOOD_COST = 100
    BASE_CLAY_COST = 100
    BASE_IRON_COST = 100

    # Capacity
    CAPACITY: ClassVar[int] = 1000

    def get_capacity(self) -> int:
        return self.CAPACITY * self.level


class IronMine(ResourceBuilding):
    MAX_LEVEL = 15
    BASE_UPGRADE_TIME = timedelta(minutes=5)

    # Costs
    BASE_WOOD_COST = 100
    BASE_CLAY_COST = 80
    BASE_IRON_COST = 30

    # Producation per second
    BASE_IRON_PRODUCTION = 0.5


class ClayPit(ResourceBuilding):
    MAX_LEVEL = 15
    BASE_UPGRADE_TIME = timedelta(minutes=5)

    # Costs
    BASE_WOOD_COST = 30
    BASE_CLAY_COST = 80
    BASE_IRON_COST = 100

    # Producation per second
    BASE_CLAY_PRODUCTION = 0.5


class Sawmill(ResourceBuilding):
    MAX_LEVEL = 15
    BASE_UPGRADE_TIME = timedelta(minutes=5)

    # Costs
    BASE_WOOD_COST = 30
    BASE_CLAY_COST = 100
    BASE_IRON_COST = 80

    # Producation per second
    BASE_WOOD_PRODUCTION = 0.5


class Barracks(Building):
    MAX_LEVEL = 3
    BASE_UPGRADE_TIME = timedelta(minutes=5)

    # Costs
    BASE_WOOD_COST = 200
    BASE_CLAY_COST = 170
    BASE_IRON_COST = 90
