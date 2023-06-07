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

    def __init__(self, amount: int = 0):
        self.amount = amount

    @property
    def training_cost(self) -> dict:
        return {
            "wood": self.WOOD_COST * self.amount,
            "clay": self.CLAY_COST * self.amount,
            "iron": self.IRON_COST * self.amount,
        }

    @property
    def training_time(self) -> timedelta:
        return self.TRAINING_TIME * self.amount

    @property
    def carrying_capacity(self) -> int:
        return self.CARRYING_CAPACITY * self.amount

    @property
    def offensive_strength(self) -> int:
        return self.OFFENSIVE_STRENGTH * self.amount

    @property
    def defensive_strength(self) -> int:
        return self.DEFENSIVE_STRENGTH * self.amount

    def get_speed(self, distance_in_fields: int) -> timedelta:
        return self.SPEED * distance_in_fields


class SpearFighter(Unit):
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


class AxeFighter(Unit):
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