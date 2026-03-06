from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QGridLayout, QApplication, QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QPixmap
from assembler import Program, assemble
from ..common import Reloadable, ResetEvent, LoadProgramEvent
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
    reset_sig = Signal()
    load_program_sig = Signal(Program)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MC CPU Simulator")
        self.setWindowIcon(QPixmap("simulator/gui/assets/redstone_lamp_on.png"))
        self.pixel_display = PixelDisplay(self)
        self.keyboard = Keyboard(self)
        self.code_display = CodeDisplay(self)
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
        self.code_display.file_dropped.connect(self.load_program)

    @Slot()
    def load_program(self, fpath: str, program: Program | None = None) -> None:
        print(f"Loading new program {fpath}")
        program = program or assemble(fpath)
        self.load_program_sig.emit(program)
        event = LoadProgramEvent(program)
        app.sendEvent(self.pixel_display, event)
        app.sendEvent(self.keyboard, event)
        app.sendEvent(self.code_display, event)
        app.sendEvent(self.registers, event)
        app.sendEvent(self.ram, event)
        app.sendEvent(self.text_display, event)
        app.sendEvent(self.program_control, event)

app = QApplication([])

def launch_gui(gui: MainGUI):
    print("Launching simulator in new window")
    gui.show()
    app.exec()
