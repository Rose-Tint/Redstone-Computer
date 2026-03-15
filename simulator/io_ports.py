from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import QWidget
from assembler import ast
from .common import Word, clamp_word
from .error import InvalidPort


class Port(QObject):
    input_read = Signal()
    output_written = Signal(int)

    def __init__(self, parent: "IOPorts", number: int):
        super().__init__(parent)
        self.number = number
        self.input: Word = 0
        self.output: Word = 0

    def write_input(self, value: Word) -> None:
        self.input = clamp_word(value)

    def read_input(self) -> Word:
        self.input_read.emit()
        return self.input

    def write_output(self, value: Word) -> None:
        self.output = clamp_word(value)
        self.output_written.emit(value)

    def read_output(self) -> Word:
        return self.output

class IOPorts(QObject):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.ports: list[Port] = [Port(self, n) for n in range(16)]

    def __getitem__(self, port: int | ast.Define) -> Port:
        if 0 > port or port > 15 :
            raise InvalidPort(port)
        else:
            return self.ports[int(port)]
