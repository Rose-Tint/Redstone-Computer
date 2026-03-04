from .common import *
from .data import *
from .macro import *


ResolvedCode: TypeAlias = list[Instruction]

@dataclass
class Import:
    path: str

@dataclass
class Assembly:
    data_segment: DataSegment
    code_segment: ResolvedCode

    def __repr__(self) -> str:
        s = ".code\n"
        for ins in self.code_segment:
            s += f"\t{repr(ins)}\n"
        return s
