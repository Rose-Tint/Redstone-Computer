from enum import Enum
from typing import overload


class Pos:
    def __init__(self, x: int, y: int, z: int) -> None:
        self.x: int = x
        self.y: int = y
        self.z: int = z

    def __add__(self, other):
        if isinstance(other, Pos):
            return self.with_offset(other.x, other.y, other.z)
        elif isinstance(other, tuple):
            return self.with_offset(other[0], other[1], other[2])

    def with_offset(self, x = None, y = None, z = None):
        if isinstance(x, Pos):
            return Pos(self.x + x.x, self.y + x.y, self.z + x.z)
        if isinstance(x, tuple):
            return Pos(self.x + x[0], self.y + x[1], self.z + x[2])
        else:
            x = x or 0; y = y or 0; z = z or 0
            return Pos(self.x + x, self.y + y, self.z + z)

    def tuple(self) -> tuple[int, int, int]:
        return (self.x, self.y, self.z)

    def copy(self):
        return Pos(self.x, self.y, self.z)

    @classmethod
    def parse(cls, s: str):
        nums = s.split(',')
        if len(nums) != 3:
            raise ValueError(f"Invalid position, wrong number of values: '{nums}'")
        x, y, z = [int(n.strip()) for n in nums]

    def __repr__(self) -> str:
        return f"Pos({self.x}, {self.y}, {self.z})"


