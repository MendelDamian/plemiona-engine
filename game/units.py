from datetime import timedelta
from typing import ClassVar


class Unit:
    # time to travel one field
    SPEED: ClassVar[timedelta] = timedelta(seconds=1)

    # Time to train in seconds
    TRAINING_TIME: ClassVar[timedelta] = timedelta(seconds=5)

    # Costs per unit
    WOOD_COST: ClassVar[int] = 0
    CLAY_COST: ClassVar[int] = 0
    IRON_COST: ClassVar[int] = 0

    # Carring capacity per unit
    CARRYING_CAPACITY: ClassVar[int] = 0

    # Offensive and defensive strength
    OFFENSIVE_STRENGTH: ClassVar[int] = 0
    DEFENSIVE_STRENGTH: ClassVar[int] = 0

    def __init__(self, count: int = 0):
        self.count = count

    @classmethod
    def get_training_cost(cls, unit_count: int) -> dict[str, int]:
        return {
            "wood": cls.WOOD_COST * unit_count,
            "clay": cls.CLAY_COST * unit_count,
            "iron": cls.IRON_COST * unit_count,
        }

    @classmethod
    def get_training_time(cls, unit_count: int) -> timedelta:
        return cls.TRAINING_TIME * unit_count

    @property
    def get_carrying_capacity(self) -> int:
        return self.CARRYING_CAPACITY * self.count

    @property
    def get_offensive_strength(self) -> int:
        return self.OFFENSIVE_STRENGTH * self.count

    @property
    def get_defensive_strength(self) -> int:
        return self.DEFENSIVE_STRENGTH * self.count

    def get_speed(self, distance_in_fields: float) -> timedelta:
        return self.SPEED * distance_in_fields


class Spearman(Unit):
    SPEED = timedelta(seconds=18)
    TRAINING_TIME = timedelta(seconds=5)

    WOOD_COST = 50
    CLAY_COST = 30
    IRON_COST = 10

    CARRYING_CAPACITY = 25

    OFFENSIVE_STRENGTH = 10
    DEFENSIVE_STRENGTH = 15


class Swordsman(Unit):
    SPEED = timedelta(seconds=22)
    TRAINING_TIME = timedelta(seconds=7)

    WOOD_COST = 30
    CLAY_COST = 30
    IRON_COST = 70

    CARRYING_CAPACITY = 15

    OFFENSIVE_STRENGTH = 25
    DEFENSIVE_STRENGTH = 50


class Axeman(Unit):
    SPEED = timedelta(seconds=18)
    TRAINING_TIME = timedelta(seconds=7)

    WOOD_COST = 60
    CLAY_COST = 30
    IRON_COST = 40

    CARRYING_CAPACITY = 10

    OFFENSIVE_STRENGTH = 40
    DEFENSIVE_STRENGTH = 10


class Archer(Unit):
    SPEED = timedelta(seconds=18)
    TRAINING_TIME = timedelta(seconds=10)

    WOOD_COST = 100
    CLAY_COST = 30
    IRON_COST = 60

    CARRYING_CAPACITY = 10

    OFFENSIVE_STRENGTH = 15
    DEFENSIVE_STRENGTH = 50


UNITS = {
    "spearman": Spearman,
    "swordsman": Swordsman,
    "axeman": Axeman,
    "archer": Archer,
}
