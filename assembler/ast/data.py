from .common import *
# from collections import OrderedDict


Data: TypeAlias = list[int]

@dataclass
class DataDef:
    label: Label
    data: Data

# class DataSegment(OrderedDict): pass
    # def __init__(self):
    #     self.datadefs: OrderedDict[str, Data] = OrderedDict()

DataSegment: TypeAlias = Data

@dataclass
class Align:
    to: int
