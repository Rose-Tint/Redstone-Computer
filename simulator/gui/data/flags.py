from PySide6.QtWidgets import QTableWidget, QWidget, QSizePolicy
from assembler import Program
from .common import table_cell
from ...common import Reloadable


class Flags(QTableWidget, Reloadable):
    def __init__(self, parent: QWidget):
        super().__init__(1, 3, parent)
        self.setHorizontalHeaderLabels(["Overflow", "Negative", "Zero"])
        self.reset()
        self.verticalHeader().hide()
        # self.resizeColumnsToContents()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.adjustSize()

    def set_flags(self, overflow: bool, negative: bool, zero: bool):
        self.setItem(0, 0, table_cell(int(overflow)))
        self.setItem(0, 1, table_cell(int(negative)))
        self.setItem(0, 2, table_cell(int(zero)))

    def reset(self) -> None:
        self.set_flags(False, False, False)

    def load_program(self, program: Program) -> None:
        return None
