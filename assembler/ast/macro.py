from typing import TypeAlias
from dataclasses import dataclass
from .common import Name, InstrArg, LabelDecl, Immediate, Register, Label
from .meta import Meta, HasMeta
from .instructions import Instruction, RegEncoded, ImmEncoded, JumpEncoded, SpecEncoded, CodeSegment


class MacroParam(Name):
    pass

_MacroInstrArg: TypeAlias = Register | Immediate | MacroParam

MacroStatement: TypeAlias = LabelDecl | Instruction

MacroBody: TypeAlias= list[MacroStatement]

class Macro(HasMeta):
    def __init__(self, name: Name, params: list[MacroParam], body: MacroBody):
        self.name: Name = name
        self.params: list[MacroParam] = params
        self.body: MacroBody = body
        self.instance: int = 0

    def __repr__(self) -> str:
        return f".macro {self.name} {' '.join(map(str, self.params))} ..."

    def generate_label(self, orig: Label) -> Label:
        inst = self.instance
        self.instance += 1
        orig.name += f"_LOCAL_{inst}"
        return orig

    @property
    def meta(self) -> Meta:
        return self.name.meta

    @meta.setter
    def meta(self, new: Meta) -> None:
        self.name.meta = new

class MacroCall(HasMeta):
    def __init__(self, name: Name, args: list[Register | Immediate]):
        self.name: Name = name
        self.args: list[Register | Immediate] = args

    def __repr__(self) -> str:
        return f"{self.name} {' '.join(map(str, self.args))}"

    @property
    def meta(self) -> Meta:
        return self.name.meta

    @meta.setter
    def meta(self, new: Meta) -> None:
        self.name.meta = new

class MacroCallArgs:
    def __init__(self, name: Name, params: list[MacroParam], args: list[InstrArg]):
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
            stmt.label: Label = macro.generate_label(stmt.label)
        elif isinstance(stmt, RegEncoded):
            stmt.rs: InstrArg = argdict[stmt.rs]
            stmt.rt: InstrArg = argdict[stmt.rt]
            stmt.rd: InstrArg = argdict[stmt.rd]
        elif isinstance(stmt, ImmEncoded):
            stmt.rs: InstrArg = argdict[stmt.rs]
            stmt.rt: InstrArg = argdict[stmt.rt]
            stmt.imm: InstrArg = argdict[stmt.imm]
        elif isinstance(stmt, JumpEncoded):
            stmt.label: InstrArg = argdict[stmt.label]
            # stmt.addr = argdict[stmt.addr]
        elif isinstance(stmt, SpecEncoded):
            stmt.rs: InstrArg = argdict[stmt.rs]
            stmt.port: InstrArg = argdict[stmt.port]
            stmt.imm: InstrArg = argdict[stmt.imm]
        else:
            raise ValueError(f"invalid statement in macro {repr(call)}")
        body.append(stmt)
    return body
