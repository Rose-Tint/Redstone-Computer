from dataclasses import dataclass
from typing import TypeAlias
from .meta import Meta, HasMeta
from .common import Label


Data: TypeAlias = list[int]

@dataclass
class DataDef(HasMeta):
    _meta: Meta
    label: Label
    data: Data

    @property
    def meta(self) -> Meta:
        return self._meta

DataSegment: TypeAlias = Data
# @dataclass
# class DataSegment:
#     meta: Meta
#     data: Data


@dataclass
class Align:
    to: int
