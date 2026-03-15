from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLineEdit, QGridLayout, QLabel
from .common import Reloadable
from .io_ports import Port, Slot


class TextDisplay(QWidget, Reloadable):
    def __init__(self, parent: QWidget, buffer_p: Port, control_p: Port):
        super().__init__(parent)
        self._buffer: str = ""
        self.buffer_port: Port = buffer_p
        self.control_port: Port = control_p
        self.buffer_port.output_written.connect(self.push_character)
        self.control_port.output_written.connect(self.push_buffer)
        self.control_port.input_read.connect(self.clear_buffer)
        self.buffer_widget = QLineEdit(self, readOnly=True)
        self.display_widget = QLineEdit(self, readOnly=True)
        grid = QGridLayout(self)
        grid.addWidget(QLabel("Buffer", self), 0, 0)
        grid.addWidget(self.buffer_widget, 0, 1)
        grid.addWidget(QLabel("Display", self), 1, 0)
        grid.addWidget(self.display_widget, 1, 1, 1, -1)
        grid.setColumnStretch(1, 2)
        display_height = 2 * grid.rowMinimumHeight(0)
        grid.setRowMinimumHeight(1, display_height)
        grid.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(grid)

    @Slot()
    def push_character(self, value: int) -> None:
        self.buffer += chr(value)

    @Slot()
    def push_buffer(self, _value: int | None = None) -> None:
        self.display_widget.setText(self.buffer)
        self.clear_buffer()

    @Slot()
    def clear_buffer(self) -> None:
        self.buffer = ""

    def reset(self) -> None:
        self.clear_buffer()
        self.push_buffer()
