import enum
from PySide6.QtWidgets import QTableWidget, QWidget, QSizePolicy
from assembler import Program
from .common import table_cell, Reloadable, TableCell


class ALUFlags(enum.IntFlag):
    Overflow = 1
    Zero = 2
    Negative = 4

    @classmethod
    def Empty(cls) -> "ALUFlags":
        return ALUFlags(0)

    def __repr__(self) -> str:
        return f"[oflow: {ALUFlags.Overflow in self}, zero: {ALUFlags.Zero in self}, neg: {ALUFlags.Negative in self}]"

    @classmethod
    def cmp(cls, value: int) -> "ALUFlags":
        flags = cls.Empty()
        if value > 0:
            flags |= ALUFlags.Overflow
        if value < 0:
            flags |= ALUFlags.Negative
        if value == 0:
            flags |= ALUFlags.Zero
        return flags

    def set_overflow(self, to: bool) -> None:
        if to:
            self |= ALUFlags.Overflow
        else:
            self &= ~ALUFlags.Overflow

    def set_zero(self, to: bool) -> None:
        if to:
            self |= ALUFlags.Zero
        else:
            self &= ~ALUFlags.Zero

    def set_negative(self, to: bool) -> None:
        if to:
            self |= ALUFlags.Negative
        else:
            self &= ~ALUFlags.Negative

class FlagsWidget(QTableWidget, Reloadable):
    def __init__(self, parent: QWidget):
        super().__init__(1, 3, parent)
        self._alu_flags = ALUFlags.Empty()
        self.setHorizontalHeaderLabels(ALUFlags._member_names_)
        self.reset()
        self.verticalHeader().hide()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.adjustSize()

    @property
    def alu_flags(self) -> ALUFlags:
        return self._alu_flags

    @alu_flags.setter
    def alu_flags(self, flags: ALUFlags) -> None:
        self.setCellWidget(0, 0, TableCell(self, int(ALUFlags.Overflow in flags)))
        self.setCellWidget(0, 1, TableCell(self, int(ALUFlags.Zero in flags)))
        self.setCellWidget(0, 2, TableCell(self, int(ALUFlags.Negative in flags)))
        self._alu_flags = flags

    def reset(self) -> None:
        self.alu_flags = ALUFlags.Empty()
