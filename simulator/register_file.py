from PySide6.QtWidgets import QTableWidget, QWidget, QSizePolicy
from assembler import Program, ast
from .common import table_cell, Word, Reloadable, InterpreterError, clamp_word, WRITE_COLOR, TableCell


class RegisterFile(QTableWidget, Reloadable):
    def __init__(self, parent: QWidget):
        super().__init__(1, 7, parent)
        self.registers: list[Word] = [0] * 7
        # self.prev_written_reg: TableCell | None = None
        for i, value in enumerate(self.registers):
            self.setCellWidget(0, i, TableCell(self, value))
            self.write(i, value, animate=False)
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

    def write(self, register: ast.Register | int, value: Word, animate: bool = True) -> None:
        if isinstance(register, ast.Register):
            register = register.value
        if register == 0:
            return # writing to $zero does nothing
        elif register > 7 or register < 0:
            raise InterpreterError(f"invalid register {register}")
        else:
            value = clamp_word(value)
            self.registers[register] = value
            cell: TableCell = self.cellWidget(0, register - 1) # type: ignore
            cell.value = value
            # cell = TableCell(self, value)
            # self.setCellWidget(0, register - 1, cell)
            # if animate:
            #     if self.prev_written_reg is not None:
            #         self.prev_written_reg.reset_background()
            #     cell.set_background(WRITE_COLOR)
            #     self.prev_written_reg = cell

    def update_registers(self, registers: list[int]) -> None:
        registers = registers[1:] if len(registers) == 8 else registers
        assert len(registers) == 7, f"invalid register count: {len(registers)}"
        for i, value in enumerate(registers):
            self.write(i, value, animate=False)

    def reset(self) -> None:
        self.update_registers([0] * 7)

