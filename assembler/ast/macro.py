from typing import TypeAlias
from dataclasses import dataclass
from .common import InstrArg, LabelDecl, Immediate, Register, Label
from .meta import Meta, HasMeta
from .instructions import Instruction, RegEncoded, ImmEncoded, JumpEncoded, SpecEncoded, CodeSegment


class MacroParam(HasMeta):
    def __init__(self, meta: Meta, name: str):
        self._meta: Meta = meta
        self.name: str = name

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return str.__hash__(self.name)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, MacroParam):
            return self.name == other.name
        else:
            return self.name == other

    @property
    def meta(self) -> Meta:
        return self._meta

_MacroInstrArg: TypeAlias = Register | Immediate | MacroParam

MacroStatement: TypeAlias = LabelDecl | Instruction

@dataclass
class Macro(HasMeta):
    _meta: Meta
    name: str
    params: list[MacroParam]
    body: list[MacroStatement]
    instance: int = 0

    def generate_label(self, name: Label) -> Label:
        return Label(name._meta, f"{name}_LOCAL_{self.instance}")

    @property
    def meta(self) -> Meta:
        return self._meta

@dataclass
class MacroCall(HasMeta):
    _meta: Meta
    name: str
    args: list[Register | Immediate]

    @property
    def meta(self) -> Meta:
        return self._meta

class MacroCallArgs:
    def __init__(self, name: str, params: list[MacroParam], args: list[InstrArg]):
        if len(params) != len(args):
            params_str = ", ".join(map(str, params))
            raise ValueError(
                f"Parse error: incorrect argument amount for {name} {params_str}\
                \texpected {len(params)}, got {len(args)}"
                )
        self.data: dict[MacroParam, InstrArg] = dict(zip(params, args))

    def __getitem__(self, arg: _MacroInstrArg) -> InstrArg:
        if isinstance(arg, MacroParam):
            return self.data[arg]
        else:
            return arg

def expand_macro(macro: Macro, call: MacroCall) -> CodeSegment:
    body: CodeSegment = []
    argdict = MacroCallArgs(macro.name, macro.params, call.args)
    for stmt in macro.body:
        if isinstance(stmt, LabelDecl):
            stmt.label = macro.generate_label(stmt.label)
        elif isinstance(stmt, Instruction):
            if isinstance(stmt, RegEncoded):
                stmt.rs = argdict[stmt.rs]
                stmt.rt = argdict[stmt.rt]
                stmt.rd = argdict[stmt.rd]
            elif isinstance(stmt, ImmEncoded):
                stmt.rs = argdict[stmt.rs]
                stmt.rt = argdict[stmt.rt]
                stmt.imm = argdict[stmt.imm]
            elif isinstance(stmt, JumpEncoded):
                stmt.label = argdict[stmt.label]
                # stmt.addr = argdict[stmt.addr]
            elif isinstance(stmt, SpecEncoded):
                stmt.rs = argdict[stmt.rs]
                stmt.port = argdict[stmt.port]
                stmt.imm = argdict[stmt.imm]
            else:
                raise ValueError(f"invalid instruction in macro {repr(call)}")
        else:
            raise ValueError(f"invalid statement in macro {repr(call)}")
        body.append(stmt)
    return body
