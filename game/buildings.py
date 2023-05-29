from datetime import timedelta
from typing import ClassVar


class Building:
    MAX_LEVEL: ClassVar[int] = 1
    BASE_UPGRADE_TIME: ClassVar[timedelta] = timedelta(minutes=1)

    # Upgrade costs
    WOOD_COST: ClassVar[int] = 0
    CLAY_COST: ClassVar[int] = 0
    IRON_COST: ClassVar[int] = 0

    def __init__(self, level: int = 1) -> None:
        self.level = level

    def get_upgrade_cost(self) -> dict:
        return {
            "wood": self.WOOD_COST * self.level,
            "clay": self.CLAY_COST * self.level,
            "iron": self.IRON_COST * self.level,
        }

    def get_upgrade_time(self) -> timedelta:
        return self.BASE_UPGRADE_TIME * self.level

    def upgrade(self) -> None:
        if self.level < self.MAX_LEVEL:
            self.level += 1

    def downgrade(self) -> None:
        if self.level > 1:
            self.level -= 1


class ResourceBuilding(Building):
    # Producation per second
    WOOD_PRODUCATION: ClassVar[float] = 0
    CLAY_PRODUCATION: ClassVar[float] = 0
    IRON_PRODUCATION: ClassVar[float] = 0

    def get_production(self) -> dict:
        return {
            "wood": self.WOOD_PRODUCATION * self.level,
            "clay": self.CLAY_PRODUCATION * self.level,
            "iron": self.IRON_PRODUCATION * self.level,
        }


class TownHall(Building):
    MAX_LEVEL = 3
    BASE_UPGRADE_TIME = timedelta(minutes=10)

    # Costs
    WOOD_COST = 200
    CLAY_COST = 170
    IRON_COST = 90


class Granary(Building):
    MAX_LEVEL = 3
    BASE_UPGRADE_TIME = timedelta(minutes=3)

    # Costs
    WOOD_COST = 100
    CLAY_COST = 100
    IRON_COST = 100

    # Capacity
    CAPACITY: ClassVar[int] = 1000

    def get_capacity(self) -> int:
        return self.CAPACITY * self.level


class IronMine(ResourceBuilding):
    MAX_LEVEL = 3
    BASE_UPGRADE_TIME = timedelta(minutes=5)

    # Costs
    WOOD_COST = 100
    CLAY_COST = 80
    IRON_COST = 30

    # Producation per second
    IRON_PRODUCATION = 0.5


class ClayPit(ResourceBuilding):
    MAX_LEVEL = 3
    BASE_UPGRADE_TIME = timedelta(minutes=5)

    # Costs
    WOOD_COST = 30
    CLAY_COST = 80
    IRON_COST = 100

    # Producation per second
    CLAY_PRODUCATION = 0.5


class Sawmill(ResourceBuilding):
    MAX_LEVEL = 3
    BASE_UPGRADE_TIME = timedelta(minutes=5)

    # Costs
    WOOD_COST = 30
    CLAY_COST = 100
    IRON_COST = 80

    # Producation per second
    WOOD_PRODUCATION = 0.5


class Barracks(Building):
    MAX_LEVEL = 3
    BASE_UPGRADE_TIME = timedelta(minutes=5)

    # Costs
    WOOD_COST = 200
    CLAY_COST = 170
    IRON_COST = 90
