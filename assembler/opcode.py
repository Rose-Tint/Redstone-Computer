from enum import Enum, IntEnum

class Opcode(IntEnum):
    NOOP = 0b00000
    ADD = 0b00001
    SUB = 0b00010
    CMP = 0b00011
    AND = 0b00100
    OR  = 0b00101
    XOR = 0b00110
    NOR = 0b00111
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

    @classmethod
    def mneumonics(cls) -> list[str]:
        return [op.lower() for op in cls._member_names_]

    @classmethod
    def get(cls, name: str):
        return cls.__getitem__(name.upper())

    def __str__(self) -> str:
        return self.name

    __repr__ = __str__

    def is_register_encoded(self):
        c = self.__class__
        return self in [c.NOOP, c.ADD, c.SUB, c.CMP, c.AND, c.OR, c.XOR, c.NOR]

    def is_immediate_encoded(self):
        c = self.__class__
        return self in [c.SHL, c.SHR, c.LW, c.SW, c.LI, c.CMPI, c.ADDI, c.SUBI]

    def is_jump_encoded(self):
        c = self.__class__
        return self in [c.JUMP, c.CALL, c.BGT, c.BRO, c.BGE, c.BNO, c.BLT, c.BRN, c.BLE, c.BNN, c.BEQ, c.BRZ, c.BNE, c.BNZ]
