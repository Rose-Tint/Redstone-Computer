from copy import copy
from typing import Generic, overload, final
from abc import ABC, abstractmethod
from dataclasses import dataclass
import lark
from utils import T


@dataclass
class Meta:
    filepath: str
    line: int
    column: int

    @classmethod
    def mk_intrinsic(cls) -> "Meta":
        return cls("", 0, 0)

    @classmethod
    def from_lark(cls, obj: lark.Token | lark.Tree) -> "Meta":
        if isinstance(token := obj, lark.Token):
            return Meta(
                getattr(token, "file", None) or "",
                token.line or 0,
                token.column or 0
            )
        elif isinstance(tree := obj, lark.Tree):
            return Meta(
                getattr(tree, "file", None) or "",
                tree.meta.line,
                tree.meta.column
            )
        else:
            raise ValueError(
                f"Meta.from_lark: expected Token or Tree, but got {type(obj).__name__}"
                )

    def __eq__(self, other) -> bool:
        if (meta := get_meta(other)) is not None:
            eq: bool = self.filepath == meta.filepath
            eq &= self.line == meta.line
            eq &= self.column == meta.column
            return eq
        else:
            raise TypeError(f"Meta.__eq__: cannot compare with {type(other)}")

    def is_instrinsic(self) -> bool:
        return self.filepath == ""

    def context_from_file(self, full_line: bool = False):
        if self.is_instrinsic():
            raise ValueError("Meta object is empty")
        with open(self.filepath) as file:
            return self.context(file.read(), full_line)

    def context(self, contents: str, full_line: bool = False):
        ...

class HasMeta:
    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls)
        self._meta: Meta
        setattr(self, "_meta", None)
        return self

    def __init__(self, meta: Meta):
        self._meta = meta

    @property
    def meta(self) -> Meta:
        return self._meta

    @meta.setter
    def meta(self, new: Meta) -> None:
        self._meta = new

    @final
    def is_intrinsic(self) -> bool:
        return self.meta.is_instrinsic()

    @final
    def __matmul__(self, arg):
        if (new_meta := get_meta(arg)) is not None:
            cpy = copy(self)
            cpy.meta = new_meta
            return cpy
        else:
            cls = self.__class__
            raise TypeError(f"{cls}.__matmul__: {type(arg)} does not have metadata")

def get_meta(obj) -> Meta | None:
    if isinstance(obj, HasMeta):
        return obj.meta
    elif isinstance(obj, (lark.Token, lark.Tree)):
        return Meta.from_lark(obj)
    else:
        return None

def has_meta(obj) -> bool:
    return get_meta(obj) is not None

class Located(Generic[T], HasMeta):
    # _meta: Meta
    # data: T
    def __init__(self, data: T, meta: Meta | None = None):
        if has_meta(data):
            raise Warning(f"Located[{type(data)}].__init__: data already has metadata; using `Located` is redundant")
        elif meta is None:
            raise ValueError(f"Located[{type(data)}].__init__: if `data` does not have metadata, `meta` cannot be None")
        self.data = data
        self._meta = meta
