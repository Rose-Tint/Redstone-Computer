from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidgetItem

def empty_cell() -> QTableWidgetItem:
    return QTableWidgetItem()

def table_cell(value: int) -> QTableWidgetItem:
    item = QTableWidgetItem(str(value))
    item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
    return item

