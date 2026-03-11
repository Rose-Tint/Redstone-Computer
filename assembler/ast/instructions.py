from typing import TypeVar, TypeAlias
from dataclasses import dataclass
from .common import Register, Immediate, Label, LabelDecl, Define
from .meta import Meta, HasMeta
from ..opcode import Opcode


Unresolved = TypeVar("Unresolved")
Register_T: TypeAlias = Register | Unresolved
Immediate_T: TypeAlias = Immediate | Unresolved
Label_T: TypeAlias = Label | Unresolved

@dataclass(init=False)
class Instruction(HasMeta):
    _meta: Meta
    opcode: Opcode

    def __init__(self, meta: Meta, opcode: str):
        self._meta = meta
        self.opcode: Opcode = Opcode.get(opcode)

    def assert_symbol_resolved(self, value, *exp_types: type):
        if not isinstance(value, exp_types):
            raise ValueError(
                f"Unresolved symbol {value} (type: {type(value)}) in {repr(self)}"
            )

    def assert_resolved(self):
        self.assert_symbol_resolved(self.opcode, Opcode)

    def machine_code(self) -> int:
        self.assert_resolved()
        # if not self.assert_resolved():
            # raise ValueError(f"Unresolved symbol in `{repr(self)}`")
        return self.opcode << 11

    def machine_code_str(self) -> str:
        code = self.machine_code()
        return bin(code)[2:].rjust(16, '0')

    @property
    def meta(self) -> Meta:
        return self._meta

@dataclass
class RegEncoded(Instruction):
    rs: Register_T
    rt: Register_T
    rd: Register_T

    def assert_resolved(self):
        super().assert_resolved()
        self.assert_symbol_resolved(self.rs, Register, int)
        self.assert_symbol_resolved(self.rt, Register, int)
        self.assert_symbol_resolved(self.rd, Register, int)

    def __repr__(self) -> str:
        return f"{self.opcode} {self.rd} {self.rs} {self.rt}"

    def machine_code(self) -> int:
        result = super().machine_code()
        result |= self.rs << 8
        result |= self.rt << 5
        result |= self.rd << 2
        return result

@dataclass
class ImmEncoded(Instruction):
    rs: Register_T
    rt: Register_T
    imm: Immediate_T

    def assert_resolved(self):
        super().assert_resolved()
        self.assert_symbol_resolved(self.rs, Register, int)
        self.assert_symbol_resolved(self.rt, Register, int)
        self.assert_symbol_resolved(self.imm, int, Define)

    def __repr__(self) -> str:
        if self.opcode is Opcode.LI or self.opcode is Opcode.CMPI:
            return f"{self.opcode} {self.rt} {self.imm}"
        elif self.opcode is Opcode.LW:
            return f"{self.opcode} {self.rt} [{self.rs}]"
        else:
            return f"{self.opcode} {self.rs} {self.rt} {self.imm}"

    def machine_code(self) -> int:
        result = super().machine_code()
        result |= self.rs << 8
        result |= self.rt << 5
        result |= self.imm # type: ignore (super().machine_code() typechecks)
        return result

@dataclass
class JumpEncoded(Instruction):
    label: Label_T
    addr: int

    def assert_resolved(self):
        super().assert_resolved()
        self.assert_symbol_resolved(self.addr, int)

    def __repr__(self) -> str:
        return f"{self.opcode} {self.label}@{self.addr}"

    def machine_code(self) -> int:
        result = super().machine_code()
        result |= self.addr
        return result

@dataclass
class SpecEncoded(Instruction):
    rs: Register_T
    port: Immediate_T = 0
    imm: Immediate_T = 0 # currently unused by any instructions

    def assert_resolved(self):
        super().assert_resolved()
        self.assert_symbol_resolved(self.rs, Register, int)
        self.assert_symbol_resolved(self.port, int, Define)
        self.assert_symbol_resolved(self.imm, int, Label, Define)
        if isinstance(self.imm, Label) and not self.imm.is_resolved():
            raise ValueError(
                f"Unresolved symbol {self.imm} (type: {type(self.imm)}) in {repr(self)}"
            )

    def __repr__(self) -> str:
        if self.opcode is Opcode.RETURN or self.opcode is Opcode.EXIT:
            return str(self.opcode)
        elif self.opcode is Opcode.PUSH or self.opcode is Opcode.POP:
            return f"{self.opcode} {self.rs}"
        else:
            return f"{self.opcode} {self.rs} {self.port}"

    def machine_code(self) -> int:
        result = super().machine_code()
        result |= self.rs << 8
        result |= self.port << 4 # type: ignore (super().machine_code() typechecks)
        result |= self.imm # type: ignore (super().machine_code() typechecks)
        return result


CodeStatement: TypeAlias = LabelDecl | Instruction

CodeSegment: TypeAlias = list[CodeStatement]

NOOP = RegEncoded(Meta(), Opcode.NOOP, 0, 0 ,0)
