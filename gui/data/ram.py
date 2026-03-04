from PySide6.QtWidgets import QTableWidget, QWidget, QSizePolicy, QScrollArea
from .common import table_cell


class RAM(QScrollArea):
    MAX_SIZE = 255

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.table = QTableWidget(self.MAX_SIZE // 4, 4, self)
        hheader = self.table.horizontalHeader()
        hheader.setSectionResizeMode(hheader.ResizeMode.Stretch)
        vheader = self.table.verticalHeader()
        vheader.setSectionResizeMode(hheader.ResizeMode.Stretch)
        self.table.setVerticalHeaderLabels([f"{i}-{i+3}" for i in range(0, self.MAX_SIZE, 4)])
        self.update_ram([0] * (self.MAX_SIZE + 1))
        # for addr in range(self.MAX_SIZE):
        #     self.write(addr, 0)
        self.table.resizeColumnsToContents()
        self.table.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.table.adjustSize()
        self.setWidget(self.table)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def write(self, addr: int, value: int) -> None:
        row = addr // 4
        column = addr % 4
        self.table.setItem(column, row, table_cell(value))

    def update_ram(self, ram: list[int]) -> None:
        assert len(ram) == self.MAX_SIZE + 1
        for addr, value in enumerate(ram):
            self.write(addr, value)
