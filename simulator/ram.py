from PySide6.QtWidgets import QTableWidget, QWidget, QSizePolicy, QScrollArea, QTableWidgetItem
from assembler import Program
from .common import Reloadable, Word, Addr, table_cell


class RAM(QScrollArea, Reloadable):
    MAX_SIZE = 256

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.data: list[Word] = [0] * self.MAX_SIZE
        self.table = QTableWidget(self.MAX_SIZE // 4, 4, self)
        # hheader = self.table.horizontalHeader()
        # hheader.setSectionResizeMode(hheader.ResizeMode.Stretch)
        # vheader = self.table.verticalHeader()
        # vheader.setSectionResizeMode(hheader.ResizeMode.Stretch)
        self.table.setVerticalHeaderLabels(
            [f"{i} - {i+3}" for i in range(0, self.MAX_SIZE, 4)]
            )
        self.reset()
        self.table.resizeColumnsToContents()
        self.table.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.table.adjustSize()
        self.setWidget(self.table)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def read(self, addr: Addr) -> Word:
        return self.data[addr]

    def write(self, addr: Addr, value: Word) -> None:
        self.data[addr] = value
        row = addr // 4
        column = addr % 4
        cell = table_cell(value)
        cell.setToolTip(f"Address: {addr}")
        self.table.setItem(row, column, cell)

    def update_ram(self, ram: list[Word]) -> None:
        assert len(ram) == self.MAX_SIZE, f"ram length: {len(ram)}"
        for addr, value in enumerate(ram):
            self.write(addr, value)

    def reset(self) -> None:
        self.update_ram([0] * self.MAX_SIZE)

    def load_program(self, program: Program) -> None:
        data = program.data + [0] * (self.MAX_SIZE - len(program.data))
        self.update_ram(data)
        # for addr, value in enumerate(program.data):
        #     self.write(addr, value)
