from typing import TypeVar, TypeAlias, Generic
from .common import Register, Immediate, Label, LabelDecl, Define, Zero, Addr
from .meta import Meta, HasMeta
from .opcode import Opcode, OpcodeEnum, NOOP_OPCODE


Unresolved_T = TypeVar("Unresolved_T")
Reg_T: TypeAlias = Register | Unresolved_T
Imm_T: TypeAlias = Immediate | Unresolved_T
Lbl_T: TypeAlias = Label | Unresolved_T

class Instruction(HasMeta):
    def __init__(self, opcode: Opcode):
        self.opcode: Opcode = opcode

    def assert_symbol_resolved(self, value, *exp_types: type):
        if not isinstance(value, exp_types):
            raise ValueError(
                f"Unresolved symbol {value} (type: {type(value)}) in {repr(self)}"
            )

    def assert_resolved(self):
        self.assert_symbol_resolved(self.opcode, Opcode)

    def machine_code(self) -> int:
        self.assert_resolved()
        return int(self.opcode) << 11

    def machine_code_str(self) -> str:
        code = self.machine_code()
        return bin(code)[2:].rjust(16, '0')

    @property
    def meta(self) -> Meta:
        return self.opcode.meta

    @meta.setter
    def meta(self, new: Meta):
        self.opcode.meta = new

class RegEncoded(Instruction):
    def __init__(self, opcode: Opcode, rs: Reg_T, rt: Reg_T, rd: Reg_T):
        super().__init__(opcode)
        self.rs: Reg_T = rs
        self.rt: Reg_T = rt
        self.rd: Reg_T = rd

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

class ImmEncoded(Instruction):
    def __init__(self, opcode: Opcode, rs: Reg_T, rt: Reg_T, imm: Imm_T):
        super().__init__(opcode)
        self.rs: Reg_T = rs
        self.rt: Reg_T = rt
        self.imm: Imm_T = imm

    def assert_resolved(self):
        super().assert_resolved()
        self.assert_symbol_resolved(self.rs, Register, int)
        self.assert_symbol_resolved(self.rt, Register, int)
        self.assert_symbol_resolved(self.imm, int, Define)

    def __repr__(self) -> str:
        if self.opcode == OpcodeEnum.LI or self.opcode == OpcodeEnum.CMPI:
            return f"{self.opcode} {self.rt} {self.imm}"
        elif self.opcode == OpcodeEnum.LW:
            return f"{self.opcode} {self.rt} [{self.rs}]"
        else:
            return f"{self.opcode} {self.rs} {self.rt} {self.imm}"

    def machine_code(self) -> int:
        result = super().machine_code()
        result |= self.rs << 8
        result |= self.rt << 5
        result |= int(self.imm)
        return result

class JumpEncoded(Instruction):
    def __init__(self, opcode: Opcode, label: Lbl_T, addr: Addr):
        super().__init__(opcode)
        self.label: Lbl_T = label
        self.addr: Addr = addr

    def assert_resolved(self):
        super().assert_resolved()
        self.assert_symbol_resolved(self.addr, int)

    def __repr__(self) -> str:
        return f"{self.opcode} {self.label}@{self.addr}"

    def machine_code(self) -> int:
        result = super().machine_code()
        result |= self.addr
        return result

class SpecEncoded(Instruction):
    def __init__(self, opcode: Opcode, rs: Reg_T, port: Imm_T, imm: Imm_T):
        super().__init__(opcode)
        self.rs: Reg_T = rs
        self.port: Imm_T = port
        self.imm: Imm_T = imm

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
        if self.opcode == OpcodeEnum.RETURN or self.opcode == OpcodeEnum.EXIT:
            return str(self.opcode)
        elif self.opcode == OpcodeEnum.PUSH or self.opcode == OpcodeEnum.POP:
            return f"{self.opcode} {self.rs}"
        else:
            return f"{self.opcode} {self.rs} {self.port}"

    def machine_code(self) -> int:
        result = super().machine_code()
        result |= self.rs << 8
        result |= int(self.port) << 4
        result |= int(self.imm)
        return result


CodeStmt: TypeAlias = LabelDecl | Instruction

CodeSeg: TypeAlias = list[CodeStmt]

NOOP = RegEncoded(NOOP_OPCODE, Zero, Zero, Zero)
