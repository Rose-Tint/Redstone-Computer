from PySide6.QtCore import Qt, QPropertyAnimation
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QScrollArea, QWidget, QSizePolicy


def table_cell(value: int) -> QTableWidgetItem:
    item = QTableWidgetItem(str(value))
    item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
    return item

class Flags(QTableWidget):
    def __init__(self, parent: QWidget):
        super().__init__(1, 3, parent)
        self.setHorizontalHeaderLabels(["Overflow", "Negative", "Zero"])
        self.set_flags(False, False, False)
        self.verticalHeader().hide()
        # self.resizeColumnsToContents()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.adjustSize()

    def set_flags(self, overflow: bool, negative: bool, zero: bool):
        self.setItem(0, 0, table_cell(int(overflow)))
        self.setItem(0, 1, table_cell(int(negative)))
        self.setItem(0, 2, table_cell(int(zero)))

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

# TODO
# class Ports(QWidget):
#     def __init__(self, parent: QWidget):
#         super().__init__(parent)
#         ports = [0] * 16
#         grid = QGridLayout(self)
#         self.labels: list[QLabel] = []
#         for i, port in enumerate(ports, 1):
#             label = QLabel(self)
#             label.setText(f"$r{i+1}: {port:>3}")
#             grid.addWidget(label, i-1, 0)
#             self.labels.append(label)
#         self.setLayout(grid)

#     def update_registers(self, registers: list[int]) -> None:
#         assert len(registers) == 16
#         for i, value in enumerate(registers):
#             self.labels[i].setText(f"$r{i+1}: {value:>3}")
