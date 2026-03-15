from typing import Generic
from abc import ABC, abstractmethod
from dataclasses import dataclass
import lark
from utils import T


@dataclass
class Meta:
    filepath: str = ""
    line: int = 0
    column: int = 0

    @classmethod
    def from_token(cls, token: lark.Token) -> "Meta":
        return Meta(
            getattr(token, "file", None) or "",
            token.line or 0,
            token.column or 0
        )

    def empty(self) -> bool:
        return self.filepath == ""

    def context_from_file(self, full_line: bool = False):
        if self.empty():
            raise ValueError("Meta object is empty")
        with open(self.filepath) as file:
            return self.context(file.read(), full_line)

    def context(self, contents: str, full_line: bool = False):
        ...

@dataclass
class Located(Generic[T]):
    meta: Meta
    data: T

class HasMeta(ABC):
    @property
    @abstractmethod
    def meta(self) -> Meta:
        if hasattr(self, "meta"):
            return getattr(self, "meta")
        elif hasattr(self, "_meta"):
            return getattr(self, "_meta")
        else:
            raise NotImplemented
