from dataclasses import dataclass
from typing import Any, TypeAlias
from .meta import Meta, HasMeta


Addr: TypeAlias = int

@dataclass
class Label(HasMeta):
    _meta: Meta
    name: str
    value: int | None = None

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

    @property
    def meta(self) -> Meta:
        return self._meta

    def is_resolved(self) -> bool:
        return self.value is not None

@dataclass
class Define(HasMeta):
    _meta: Meta
    name: str
    value: int

    def __str__(self) -> str:
        return self.name

    def __int__(self) -> int:
        return self.value

    def __hash__(self) -> int:
        return hash(self.name)

    def __lshift__(self, n: int) -> int:
        return self.value << n

    def __repr__(self) -> str:
        return f"{self.name}{{{self.value}}}"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Define):
            return self.name == other.name
        elif isinstance(other, int):
            return self.value == other
        else:
            return self.name == other

    def __lt__(self, value) -> bool:
        return self.value < value

    def __gt__(self, value) -> bool:
        return self.value > value

    @property
    def meta(self) -> Meta:
        return self._meta

# class WordImmediate:
#     def __init__(self, meta: Meta, value: int = 0):
#         self.value = value
#         self.meta = meta

#     def __add__(self, value: int) -> "WordImmediate":
#         return WordImmediate(self.meta, self.value + value)

Immediate: TypeAlias = int | Label | Define

# @dataclass(init=False)
class Register(HasMeta):
    # _meta: Meta
    # id: int

    def __init__(self, name: str, meta: Meta):
        self.id = self._register_dict[name]
        self._meta = meta

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

    @property
    def meta(self) -> Meta:
        return self._meta

Zero = Register("$zero", Meta())

InstrArg: TypeAlias = Register | Immediate

@dataclass
class LabelDecl(HasMeta):
    label: Label

    def __hash__(self) -> int:
        return hash(self.label)

    @property
    def meta(self) -> Meta:
        return self.label.meta
