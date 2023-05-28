from dataclasses import dataclass
from datetime import timedelta
from typing import ClassVar


@dataclass
class Building:
    MAX_LEVEL: ClassVar[int] = 1
    level: int = 1
    base_upgrade_time: timedelta = timedelta(minutes=1)

    # Upgrade costs
    wood_cost: int = 0
    clay_cost: int = 0
    iron_cost: int = 0

    def get_upgrade_cost(self) -> dict:
        return {
            "wood": self.wood_cost * self.level,
            "clay": self.clay_cost * self.level,
            "iron": self.iron_cost * self.level,
        }

    def get_upgrade_time(self) -> timedelta:
        return self.base_upgrade_time * self.level

    def upgrade(self) -> None:
        if self.level < self.MAX_LEVEL:
            self.level += 1

    def downgrade(self) -> None:
        if self.level > 1:
            self.level -= 1


class ResourceBuilding(Building):
    # Producation per second
    wood_production: float = 0
    clay_production: float = 0
    iron_production: float = 0

    def get_production(self) -> dict:
        return {
            "wood": self.wood_production * self.level,
            "clay": self.clay_production * self.level,
            "iron": self.iron_production * self.level,
        }


@dataclass
class TownHall(Building):
    MAX_LEVEL = 3
    base_upgrade_time: timedelta = timedelta(minutes=10)

    # Costs
    wood_cost: int = 200
    clay_cost: int = 170
    iron_cost: int = 90


@dataclass
class Granary(Building):
    MAX_LEVEL = 3
    base_upgrade_time: timedelta = timedelta(minutes=3)

    # Costs
    wood_cost: int = 100
    clay_cost: int = 100
    iron_cost: int = 100

    # Capacity
    capacity: int = 1000

    def get_capacity(self) -> int:
        return self.capacity * self.level


@dataclass
class IronMine(ResourceBuilding):
    MAX_LEVEL = 3
    base_upgrade_time: timedelta = timedelta(minutes=5)

    # Costs
    wood_cost: int = 100
    clay_cost: int = 80
    iron_cost: int = 30

    # Producation per second
    iron_production: float = 0.5


@dataclass
class ClayPit(ResourceBuilding):
    MAX_LEVEL = 3
    base_upgrade_time: timedelta = timedelta(minutes=5)

    # Costs
    wood_cost: int = 30
    clay_cost: int = 80
    iron_cost: int = 100

    # Producation per second
    clay_production: float = 0.5


@dataclass
class Sawmill(ResourceBuilding):
    MAX_LEVEL = 3
    base_upgrade_time: timedelta = timedelta(minutes=5)

    # Costs
    wood_cost: int = 30
    clay_cost: int = 100
    iron_cost: int = 80

    # Producation per second
    wood_production: float = 0.5


@dataclass
class Barracks(Building):
    MAX_LEVEL = 3
    base_upgrade_time: timedelta = timedelta(minutes=5)

    # Costs
    wood_cost: int = 200
    clay_cost: int = 170
    iron_cost: int = 90
