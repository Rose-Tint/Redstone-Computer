from dataclasses import dataclass
from types import UnionType
from typing import Any, TypeAlias
from .meta import Meta


# Addr: TypeAlias = int

class Label:
    def __init__(self, meta: Meta, name: str, value: int | None = None):
        self.meta = meta
        self.name = name
        self.value = value

    def __str__(self) -> str:
        return self.name

    def __lshift__(self, n: int) -> int:
        assert self.value is not None
        return self.value << n

    def __repr__(self) -> str:
        if self.value is None:
            return self.name
        else:
            return f"{self.name}{{{self.value}}}"

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Label):
            return self.name == other.name
        else:
            return self.name == other

    def is_resolved(self) -> bool:
        return self.value is not None

class Define:
    def __init__(self, meta: Meta, name: str, value: int):
        self.meta: Meta = meta
        self.name: str = name
        self.value: int = value

    def __str__(self) -> str:
        return self.name

    def __int__(self) -> int:
        return self.value

    def __lshift__(self, n: int) -> int:
        return self.value << n

    def __repr__(self) -> str:
        return f"{self.name}{{{self.value}}}"

    def __ror__(self, value: Any) -> int:
        return value | self.value

    def __or__(self, value: Any) -> int:
        return self.value | value

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Define):
            return self.name == other.name
        else:
            return self.name == other

# class WordImmediate:
#     def __init__(self, meta: Meta, value: int = 0):
#         self.value = value
#         self.meta = meta

#     def __add__(self, value: int) -> "WordImmediate":
#         return WordImmediate(self.meta, self.value + value)

Immediate: TypeAlias = int | Label | Define

@dataclass(init=False)
class Register:
    meta: Meta
    id: int

    def __init__(self, name: str, meta: Meta):
        self.id = self._register_dict[name]
        self.meta = meta

    def __int__(self) -> int:
        return self.id

    def __lshift__(self, n: int) -> int:
        return self.id << n

    def __repr__(self) -> str:
        return str(list(self._register_dict.keys())[self.id])

    @classmethod
    def from_int(cls, n: int) -> "Register":
        assert 0 <= n <= 7
        return cls(list(cls._register_dict.keys())[n], Meta())

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

Zero = Register("$zero", Meta())

InstrArg: TypeAlias = Register | Immediate

@dataclass
class LabelDecl:
    label: Label

    def __hash__(self) -> int:
        return hash(self.label)
