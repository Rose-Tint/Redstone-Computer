from dataclasses import dataclass
from typing import TypeAlias, Union
from typing_extensions import Self
from enum import Enum
from ..opcode import Opcode


# Addr: TypeAlias = int

class Label(str): pass

class Define(str): pass

Immediate: TypeAlias = int | Label | Define

@dataclass(init=False)
class Register:
    value: int

    def __init__(self, name: str):
        self.value = self._register_dict[name]

    def __lshift__(self, n: int) -> int:
        return self.value << n

    def __repr__(self) -> str:
        return str(list(self._register_dict.keys())[self.value])

    @classmethod
    def from_int(cls, n: int) -> "Register":
        assert 0 <= n <= 7
        return cls(list(cls._register_dict.keys())[n])

    _register_dict = {
        "$zero": 0,
        "$r1": 1,
        "$r2": 2,
        "$r3": 3,
        "$r4": 4,
        "$r5": 5,
        "$r6": 6,
        "$r7": 7,
    }

Zero = Register("$zero")

InstrArg: TypeAlias = Register | Immediate

@dataclass
class LabelDecl:
    label: Label

    def __hash__(self) -> int:
        return hash(self.label)

