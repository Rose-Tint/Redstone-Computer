from typing import TypeAlias
from dataclasses import dataclass
from .common import Addr, Word, Define, Immediate, Name, Label, LabelDecl, Register, Zero
from .data import Align, Data, DataDef, DataSegment
from .instructions import CodeSeg, CodeStmt, Instruction, RegEncoded, ImmEncoded, JumpEncoded, SpecEncoded, NOOP
from .macro import Macro, MacroCall, MacroParam, MacroCallArgs, MacroStatement, expand_macro
from .meta import Meta, HasMeta, Located, get_meta, has_meta
from .opcode import Opcode


ResolvedCode: TypeAlias = list[Instruction]

@dataclass
class Import:
    path: str

@dataclass
class Assembly:
    data_segment: DataSegment
    code_segment: ResolvedCode
