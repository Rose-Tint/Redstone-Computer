from asyncio import Task, create_task
from collections.abc import Callable
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QGridLayout, QApplication, QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QPixmap
from assembler import Program
# from .common import QAlign
from .keyboard import Keyboard
from .pixel_display import PixelDisplay
from .code_display import CodeDisplay
from .data import RAM, RegisterFile, Flags
from .control import ProgramControl
from .text_display import TextDisplay


def make_column(parent: QWidget, *items: QWidget) -> QWidget:
    column = QWidget(parent)
    layout = QVBoxLayout(column)
    layout.setDirection(layout.Direction.TopToBottom)
    for item in items:
        layout.addWidget(item)
    column.setLayout(layout)
    return column

class MainGUI(QWidget):
    def __init__(self, program: Program):
        super().__init__()
        self.setWindowTitle("MC CPU Simulator")
        self.setWindowIcon(QPixmap("gui/assets/redstone_lamp_on.png"))
        self.pixel_display = PixelDisplay(self)
        self.keyboard = Keyboard(self)
        self.code_display = CodeDisplay(self, program.code)
        self.registers = RegisterFile(self)
        self.ram = RAM(self)
        self.program_control = ProgramControl(self)
        self.text_display = TextDisplay(self)
        self.flags = Flags(self)
        layout = QGridLayout(self)
        layout.addWidget(make_column(self,
            self.program_control,
            self.ram,
            self.code_display
            ), 0, 2, -1, 1)
        layout.addWidget(self.text_display, 0, 0)
        layout.addWidget(self.pixel_display, 1, 0, -1, 1)
        layout.addWidget(make_column(self,
            self.registers,
            self.flags,
            self.keyboard
            ), 0, 1, -1, 1)
        self.setLayout(layout)

app = QApplication([])

def launch_gui(gui: MainGUI):
    print("Launching simulator in new window")
    gui.show()
    app.exec()
