from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLineEdit, QGridLayout, QLabel


class TextDisplay(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.buffer = QLineEdit(self, readOnly=True)
        self.display = QLineEdit(self, readOnly=True)
        grid = QGridLayout(self)
        grid.addWidget(QLabel("Buffer", self), 0, 0)
        grid.addWidget(self.buffer, 0, 1)
        grid.addWidget(QLabel("Display", self), 1, 0)
        grid.addWidget(self.display, 1, 1, 1, -1)
        grid.setColumnStretch(1, 2)
        display_height = 2 * grid.rowMinimumHeight(0)
        grid.setRowMinimumHeight(1, display_height)
        grid.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(grid)


