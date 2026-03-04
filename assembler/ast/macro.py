from lark import Transformer
from .common import *
from .instructions import *


class MacroParam(str): pass

_MacroInstrArg: TypeAlias = Register | Immediate | MacroParam

MacroStatement: TypeAlias = LabelDecl | Instruction

@dataclass
class Macro:
    name: str
    params: list[MacroParam]
    body: list[MacroStatement]
    instance: int = 0

    def generate_label(self, name: Label) -> Label:
        return Label(f"{name}_LOCAL_{self.instance}")

@dataclass
class MacroCall:
    name: str
    args: list[Register | Immediate]

class MacroCallArgs:
    def __init__(self, name: str, params: list[MacroParam], args: list[InstrArg]):
        if len(params) != len(args):
            params_str = ", ".join(params)
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
            new_label = macro.generate_label(stmt.label)
            body.append(LabelDecl(new_label))
            print(f"DEBUG:     label {new_label}")
        elif isinstance(stmt, Instruction):
            if isinstance(stmt, RegEncoded):
                stmt.rs = argdict[stmt.rs] # type: ignore
                stmt.rt = argdict[stmt.rt] # type: ignore
                stmt.rd = argdict[stmt.rd] # type: ignore
            elif isinstance(stmt, ImmEncoded):
                stmt.rs = argdict[stmt.rs] # type: ignore
                stmt.rt = argdict[stmt.rt] # type: ignore
                stmt.imm = argdict[stmt.imm] # type: ignore
            elif isinstance(stmt, JumpEncoded):
                stmt.label = argdict[stmt.label] # type: ignore
                stmt.addr = argdict[stmt.addr] # type: ignore
            elif isinstance(stmt, SpecEncoded):
                stmt.rs = argdict[stmt.rs] # type: ignore
                stmt.port = argdict[stmt.port] # type: ignore
                stmt.imm = argdict[stmt.imm] # type: ignore
            raise ValueError(f"invalid instruction in macro {repr(call)}")
            body.append(stmt)
        else:
            raise ValueError(f"invalid statement in macro {repr(call)}")
    return body











# MacroArg: TypeAlias = Union[Register, int]

# @dataclass
# class Macro:
#     params: list[str]
#     body: list[Instruction]
#     instance: int

#     def generate(self, args: list[MacroArg]):
#         pass
