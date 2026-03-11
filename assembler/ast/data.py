from dataclasses import dataclass
from typing import TypeAlias
from .meta import Meta
from .common import Label


Data: TypeAlias = list[int]

@dataclass
class DataDef:
    meta: Meta
    label: Label
    data: Data

DataSegment: TypeAlias = Data
# @dataclass
# class DataSegment:
#     meta: Meta
#     data: Data


@dataclass
class Align:
    to: int
