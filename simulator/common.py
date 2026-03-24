from typing import TypeAlias
from assembler import Program
from assembler.ast import Addr, Word
from PySide6.QtCore import Qt, QEvent, QObject
from PySide6.QtWidgets import QTableWidgetItem, QTableWidget, QLabel
from PySide6.QtGui import QColor


def empty_cell() -> QTableWidgetItem:
    return QTableWidgetItem()

def table_cell(value: int) -> QTableWidgetItem:
    item = QTableWidgetItem(str(value))
    item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
    return item

class TableCell(QLabel):
    def __init__(self, parent: QTableWidget, value):
        super().__init__(str(value), parent)
        self._value = value
        self._bg_color: QColor = self.base_background

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value) -> None:
        self.setText(str(value))
        self._value = value

    @property
    def base_background(self) -> QColor:
        return self.palette().alternateBase().color()

    def set_background(self, value: QColor) -> None:
        self._bg_color = value
        style = f"background-color: #{self._bg_color.rgb():x}"
        self.setStyleSheet(style)

    def reset_background(self) -> None:
        self.set_background(self.base_background)

READ_COLOR: QColor = QColor.fromString("#0000cd")
WRITE_COLOR: QColor = QColor.fromString("#32cd32")

class StepEvent(QEvent):
    def __init__(self):
        super().__init__(QEvent.Type.User)

class ResetEvent(QEvent):
    def __init__(self):
        super().__init__(QEvent.Type.User)

class LoadProgramEvent(QEvent):
    def __init__(self, program: Program):
        super().__init__(QEvent.Type.User)
        self.program = program

class Reloadable:
    def __init_subclass__(cls: type) -> None:
        def event(self, event: QEvent, /) -> bool:
            if isinstance(event, StepEvent):
                self.reset()
                return True
            elif isinstance(event, ResetEvent):
                self.reset()
                return True
            elif isinstance(event, LoadProgramEvent):
                self.load_program(event.program)
                return True
            else:
                return super(self.__class__, self).event(event)
        if issubclass(cls, QObject):
            cls.event = event  # ty:ignore[invalid-assignment]

    def reset(self) -> None:
        return

    def load_program(self, program: Program) -> None:
        self.reset()


# def bounds_check(n: Word) -> Word:
#     if -128 > n or n > 255:
#         raise SimulatorError(f"word out of bounds ({n})")
#     else:
#         return n

def clamp(min: int, max: int, x: int) -> int:
    if x < min: x = min
    if x > max: x = max
    return x

def clamp_word(n: Word) -> Word:
    return clamp(-127, 255, n)
