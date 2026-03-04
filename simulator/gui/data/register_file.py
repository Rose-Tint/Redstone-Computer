from PySide6.QtWidgets import QTableWidget, QWidget, QSizePolicy
from .common import table_cell


class RegisterFile(QTableWidget):
    def __init__(self, parent: QWidget):
        super().__init__(1, 7, parent)
        self.update_registers([0] * 7)
        self.setHorizontalHeaderLabels([f"$r{i+1}" for i in range(7)])
        self.verticalHeader().hide()
        # self.resizeColumnsToContents()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.adjustSize()

    def write(self, register: int, value: int) -> None:
        item = table_cell(value)
        # item.setBackground(Qt.GlobalColor.green)
        self.setItem(0, register - 1, item)

    def update_registers(self, registers: list[int]) -> None:
        registers = registers[1:] if len(registers) == 8 else registers
        assert len(registers) == 7
        for i, value in enumerate(registers):
            self.write(i, value)
