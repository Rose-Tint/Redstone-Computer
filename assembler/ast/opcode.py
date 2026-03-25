from typing import Iterable, Final
from enum import Enum, IntEnum
from .meta import Meta, Located, HasMeta

class OpcodeEnum(IntEnum):
    NOOP = 0b00000
    ADD = 0b00001
    SUB = 0b00010
    CMP = 0b00011
    AND = 0b00100
    OR  = 0b00101
    XOR = 0b00110
    NOT = NOR = 0b00111
    SHL = 0b10000
    SHR = 0b10001
    LW  = 0b10010
    SW  = 0b10011
    LI  = 0b10100
    CMPI = 0b10101
    ADDI = 0b10110
    SUBI = 0b10111
    JUMP = 0b01000
    CALL = 0b01001
    BEQ = BRZ = 0b01010
    BNE = BNZ = 0b01011
    BGT = BRO = 0b01100
    BLE = BNO = 0b01101
    BLT = BRN = 0b01110
    BGE = BNN = 0b01111
    RETURN = 0b11000
    RP = 0b11010
    WP = 0b11011
    PUSH = 0b11100
    POP = 0b11101
    EXIT = 0b11111

    # @classmethod
    # def get(cls, name) -> "OpcodeEnum":
    #     return cls.__getitem__(str(name.upper()))

    def __repr__(self) -> str:
        return self._name_

class Opcode(HasMeta):
    def __init__(self, name: str, meta: Meta):
        self.code: OpcodeEnum = OpcodeEnum[name.upper()]
        self._meta: Meta = meta

    def __int__(self) -> int:
        return int(self.code)

    def __repr__(self) -> str:
        return repr(self.code)

    def __eq__(self, other) -> bool:
        if isinstance(other, OpcodeEnum):
            return self.code == other
        elif isinstance(other, Opcode):
            return self.code == other.code
        else:
            raise TypeError(f"Opcode.__eq__: cannot compare Opcode with {type(other)}")

NOOP_OPCODE: Final[Opcode] = Opcode("NOOP", Meta.mk_intrinsic())
