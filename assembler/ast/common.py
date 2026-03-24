from dataclasses import dataclass
from typing import Any, TypeAlias, overload
from lark import Token
from .meta import Meta, HasMeta


Addr: TypeAlias = int

Word: TypeAlias = int

class Name(HasMeta):
    @overload
    def __init__(self, name: Token):
        ...
    @overload
    def __init__(self, name: str, meta: Meta):
        ...
    def __init__(self, name: str | Token, meta: Meta | None = None):
        self.name: str
        if isinstance(name, Token):
            self.name = str(name)
            self.meta = Meta.from_lark(name)
        elif isinstance(name, str) and meta is not None:
            self.name = name
            self.meta = meta
        else:
            raise ValueError(
                f"Name.__init__: invalid argument types: name: {type(name)}, meta: {type(meta)}"
                )

    def __str__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Name):
            return self.name == other.name
        else:
            return self.name == other

def Intrinsic(cls, name: str) -> "Name":
    return Name(name, meta = Meta.mk_intrinsic())

class UnresolvedLabel(ValueError):
    def __init__(self, label: "Label"):
        super().__init__(f"Unresolved Label: {str(label)}")
        self.label = label

class Label(Name):
    _label_dict: dict[str, Addr] = {}

    @overload
    def __init__(self, name: Token):
        ...
    @overload
    def __init__(self, name: str, meta: Meta):
        ...
    def __init__(self, name: str | Token, meta: Meta | None = None):
        super().__init__(name, meta) # ty: ignore
        self._value: Addr | None = Label._label_dict.get(self.name, None)

    def __lshift__(self, n: int) -> int:
        return self.value << n

    def __repr__(self) -> str:
        if self.value is None:
            return str(self.name)
        else:
            return f"{self.name}{{{self.value}}}"

    def __int__(self) -> Word:
        return self.value

    @property
    def mvalue(self) -> Addr | None:
        return self._value or Label._label_dict.get(self.name, None)

    @property
    def value(self) -> Addr:
        if (value := self.mvalue) is not None:
            return value
        else:
            raise UnresolvedLabel(self)

    @value.setter
    def value(self, value: Addr) -> None:
        self._value = value
        Label._label_dict[str(self.name)] = value

    def is_resolved(self) -> bool:
        return self.mvalue is not None

@dataclass
class Define(Name):
    @overload
    def __init__(self, name: Token, value: Word):
        ...
    @overload
    def __init__(self, name: str, value: Word, meta: Meta):
        ...
    def __init__(self, name: str | Token, value: Word, meta: Meta | None = None):
        super().__init__(name, meta) # ty: ignore
        self.value: Addr = value

    def __int__(self) -> Word:
        return self.value

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

Immediate: TypeAlias = Word | Label | Define

class Register(HasMeta):
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
        return cls(list(cls._register_dict.keys())[n], Meta.mk_intrinsic())

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

Zero = Register("$zero", Meta.mk_intrinsic())

InstrArg: TypeAlias = Register | Immediate

@dataclass
class LabelDecl(HasMeta):
    def __init__(self, label: Label):
        self.label: Label = label

    def __hash__(self) -> int:
        return hash(self.label)

    def __repr__(self) -> str:
        return repr(self.label) + ":"

    @property
    def meta(self) -> Meta:
        return self.label.meta

    @meta.setter
    def meta(self, new: Meta) -> None:
        self.label.meta = new
