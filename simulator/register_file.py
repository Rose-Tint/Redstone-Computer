from PySide6.QtWidgets import QTableWidget, QWidget, QSizePolicy
from assembler import Program, ast
from .common import table_cell, Word, Reloadable, InterpreterError, clamp_word


class RegisterFile(QTableWidget, Reloadable):
    def __init__(self, parent: QWidget):
        super().__init__(1, 7, parent)
        self.registers: list[Word] = [0] * 7
        self.setHorizontalHeaderLabels([f"$r{i+1}" for i in range(7)])
        self.verticalHeader().hide()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.adjustSize()

    def read(self, register: ast.Register | int) -> Word:
        if isinstance(register, ast.Register):
            register = register.value
        if register > 7 or register < 0:
            raise InterpreterError(f"invalid register {register}")
        elif register == 0:
            return 0
        else:
            return self.registers[register]

    def write(self, register: ast.Register | int, value: Word) -> None:
        if isinstance(register, ast.Register):
            register = register.value
        if register == 0:
            return # writing to $zero does nothing
        elif register > 7 or register < 0:
            raise InterpreterError(f"invalid register {register}")
        else:
            value = clamp_word(value)
            self.registers[register] = value
            item = table_cell(value)
            self.setItem(0, register - 1, item)

    def update_registers(self, registers: list[int]) -> None:
        registers = registers[1:] if len(registers) == 8 else registers
        assert len(registers) == 7
        for i, value in enumerate(registers):
            self.write(i, value)

    def reset(self) -> None:
        self.update_registers([0] * 7)

