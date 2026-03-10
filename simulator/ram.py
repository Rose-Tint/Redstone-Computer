from PySide6.QtWidgets import QTableWidget, QWidget, QSizePolicy, QScrollArea, QTableWidgetItem
from assembler import Program
from .common import Reloadable, Word, Addr, READ_COLOR, WRITE_COLOR, TableCell
from .error import InvalidRAMAddress


class RAM(QScrollArea, Reloadable):
    MAX_SIZE = 256

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.data: list[Word] = [0] * self.MAX_SIZE
        self.table = QTableWidget(self.MAX_SIZE // 4, 4, self)
        for addr in range(self.MAX_SIZE):
            row, col = self.addr_to_2d(addr)
            self.table.setCellWidget(row, col, TableCell(self.table, 0))
        self.table.setVerticalHeaderLabels([f"{i} - {i+3}" for i in range(0, self.MAX_SIZE, 4)])
        self.table.resizeColumnsToContents()
        self.table.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.table.adjustSize()
        self.setWidget(self.table)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    @staticmethod
    def addr_to_2d(addr: Addr) -> tuple[int, int]:
        row, column = addr // 4, addr % 4
        return (row, column)

    def read(self, addr: Addr) -> Word:
        # row, column = self.addr_to_2d(addr)
        # cell: TableCell = self.table.cellWidget(row, column) # type: ignore
        if addr >= self.MAX_SIZE:
            raise InvalidRAMAddress(addr).add_note(f"Tried to read from address {addr}")
        return self.data[addr]

    def write(self, addr: Addr, value: Word, animate: bool = True) -> None:
        if addr >= self.MAX_SIZE:
            raise InvalidRAMAddress(addr).add_note(f"Tried to write to address {addr}")
        self.data[addr] = value
        row, column = self.addr_to_2d(addr)
        cell: TableCell = self.table.cellWidget(row, column) # type: ignore
        cell.value = value
        # cell = TableCell(self.table, value)
        # cell.setToolTip(f"Address: {addr}")
        # self.table.setCellWidget(row, column, cell)
        # if animate:
            # cell.fade_background(WRITE_COLOR)

    def update_ram(self, ram: list[Word]) -> None:
        # assert len(ram) == self.MAX_SIZE, f"ram length: {len(ram)}"
        for addr, value in enumerate(ram):
            self.write(addr, value, animate=False)

    def reset(self) -> None:
        self.update_ram([0] * self.MAX_SIZE)

    def load_program(self, program: Program) -> None:
        data = program.data + [0] * (self.MAX_SIZE - len(program.data))
        self.update_ram(data)
