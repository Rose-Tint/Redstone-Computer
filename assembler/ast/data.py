from dataclasses import dataclass
from typing import TypeAlias
from .meta import Meta, HasMeta
from .common import Name


Data: TypeAlias = list[int]

class DataDef(HasMeta):
    def __init__(self, name: Name, data: Data):
        self.name: Name = name
        self.data: Data = data

    @property
    def meta(self) -> Meta:
        return self.name.meta

    @meta.setter
    def meta(self, new: Meta) -> None:
        self.name.meta = new

DataSegment: TypeAlias = Data

@dataclass
class Align:
    to: int
