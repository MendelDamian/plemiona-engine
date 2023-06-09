import math
from datetime import timedelta
from typing import ClassVar

from game import exceptions


class Building:
    MAX_LEVEL: ClassVar[int] = 15
    BASE_UPGRADE_TIME: ClassVar[timedelta] = timedelta(seconds=30)
    POINTS_PER_LEVEL: ClassVar[int] = 1

    # Multipliers
    TIME_MULTIPLIER: ClassVar[float] = 1

    # Upgrade cost coefficients
    # a * math.exp(level * COST_COEFF)
    WOOD_COST_FACTOR: ClassVar[float] = 1.0
    CLAY_COST_FACTOR: ClassVar[float] = 1.0
    IRON_COST_FACTOR: ClassVar[float] = 1.0

    COST_COEFF: ClassVar[float] = 0.23

    def __init__(self, level: int = 1) -> None:
        self.level = level

    def get_upgrade_cost(self) -> dict:
        return {
            "wood": self._get_upgrade_cost(self.WOOD_COST_FACTOR),
            "clay": self._get_upgrade_cost(self.CLAY_COST_FACTOR),
            "iron": self._get_upgrade_cost(self.IRON_COST_FACTOR),
        }

    def get_upgrade_time(self) -> timedelta:
        return self.BASE_UPGRADE_TIME * self.level * self.TIME_MULTIPLIER

    @property
    def points(self) -> int:
        return self.level * self.POINTS_PER_LEVEL

    def upgrade(self) -> None:
        if self.level < self.MAX_LEVEL:
            self.level += 1
        else:
            raise exceptions.BuildingMaxLevelException

    def downgrade(self) -> None:
        if self.level > 1:
            self.level -= 1

    def _get_upgrade_cost(self, coeff):
        return round(coeff * math.exp(self.level * Building.COST_COEFF) / 10) * 10


class TownHall(Building):
    POINTS_PER_LEVEL = 50

    # Multipliers
    TIME_MULTIPLIER = 1.2

    # Upgrade cost coefficients
    WOOD_COST_FACTOR = 71
    CLAY_COST_FACTOR = 63
    IRON_COST_FACTOR = 55


class Warehouse(Building):
    POINTS_PER_LEVEL = 30

    # Multipliers
    TIME_MULTIPLIER = 1.4

    # Upgrade cost coefficients
    WOOD_COST_FACTOR = 47
    CLAY_COST_FACTOR = 40
    IRON_COST_FACTOR = 32

    # Capacity coefficient
    CAPACITY_COEFF: ClassVar[float] = 813

    def get_capacity(self) -> int:
        return round(self.CAPACITY_COEFF * math.exp(self.level * Building.COST_COEFF) / 100) * 100


class Barracks(Building):
    MAX_LEVEL = 15
    POINTS_PER_LEVEL = 30

    # Multipliers
    TIME_MULTIPLIER = 5

    # Upgrade cost coefficients
    WOOD_COST_FACTOR = 159
    CLAY_COST_FACTOR = 133
    IRON_COST_FACTOR = 71


class ResourceBuilding(Building):
    POINTS_PER_LEVEL = 15
    BASE_UPGRADE_TIME = timedelta(seconds=15)

    # Multipliers
    TIME_MULTIPLIER = 1.3

    PRODUCTION_FACTOR: ClassVar[float] = 51.614  # per minute
    PRODUCTION_COEFF: ClassVar[float] = 0.15

    def get_production(self, seconds: float = 1.0) -> float:
        # (PRODUCTION_FACTOR * math.exp(level * PRODUCTION_COEFF) / 60) -> per second
        return self.PRODUCTION_FACTOR * math.exp(self.level * self.PRODUCTION_COEFF) / 60 * seconds


class IronMine(ResourceBuilding):
    # Upgrade cost coefficients
    WOOD_COST_FACTOR = 60
    CLAY_COST_FACTOR = 51
    IRON_COST_FACTOR = 56


class ClayPit(ResourceBuilding):
    # Upgrade cost coefficients
    WOOD_COST_FACTOR = 51
    CLAY_COST_FACTOR = 40
    IRON_COST_FACTOR = 32


class Sawmill(ResourceBuilding):
    # Upgrade cost coefficients
    WOOD_COST_FACTOR = 40
    CLAY_COST_FACTOR = 47
    IRON_COST_FACTOR = 32


BUILDINGS = {
    "town_hall": TownHall,
    "warehouse": Warehouse,
    "barracks": Barracks,
    "iron_mine": IronMine,
    "clay_pit": ClayPit,
    "sawmill": Sawmill,
}
