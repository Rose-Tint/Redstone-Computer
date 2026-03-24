import os
import sys
from typing import NoReturn
from assembler import assemble, Program, ast
from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QWidget, QMainWindow, QApplication, QGridLayout, QVBoxLayout
from PySide6.QtGui import QPixmap
from .pixel_display import PixelDisplay
from .keyboard import Keyboard
from .text_display import TextDisplay
from .control import ProgramControl
from .io_ports import IOPorts
from .cpu import CPU
from .error import SimulatorError


GUI_APPLICATION: QApplication = QApplication([])

def make_column(parent: QWidget, *items: QWidget) -> QWidget:
    column = QWidget(parent)
    layout = QVBoxLayout(column)
    layout.setDirection(layout.Direction.TopToBottom)
    for item in items:
        layout.addWidget(item)
    column.setLayout(layout)
    return column

class Simulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MC CPU Simulator")
        self.setWindowIcon(QPixmap("simulator/assets/redstone_lamp_on.png"))
        self.current_meta = ast.Meta.mk_intrinsic()
        self.current_program: Program | None = None
        self.ports = IOPorts(self)
        self.cpu = CPU(self, self.ports)
        self.pixel_display = PixelDisplay(self,
            self.ports[1],
            self.ports[2],
            self.ports[3],
            self.ports[4],
            self.ports[5]
            )
        self.keyboard = Keyboard(self, self.ports[6], self.ports[7])
        self.program_control = ProgramControl(self)
        self.text_display = TextDisplay(self, self.ports[8], self.ports[9])
        # self.program_control.step.connect(self.program_control.pause)
        self.program_control.step.connect(self.step)
        self.program_control.reload_program.connect(self.reload_program)
        self.cpu.instructions.file_dropped.connect(self.load_program)
        self.cpu.meta_update.connect(self.update_meta)
        container = QWidget(self)
        layout = QGridLayout(container)
        layout.addWidget(make_column(self,
            self.program_control,
            self.cpu.ram,
            self.cpu.instructions
            ), 0, 2, -1, 1)
        layout.addWidget(self.text_display, 0, 0)
        layout.addWidget(self.pixel_display, 1, 0, -1, 1)
        layout.addWidget(make_column(self,
            self.cpu.registers,
            self.cpu.flags_widget,
            self.keyboard
            ), 0, 1, -1, 1)
        container.setLayout(layout)
        self.setCentralWidget(container)

    @Slot()
    def update_meta(self, meta: ast.Meta) -> None:
        self.current_meta = meta

    @Slot()
    def step(self) -> None:
        try:
            self.cpu.step()
        except SimulatorError as err:
            err.set_meta(self.current_meta)

    @Slot()
    def reload_program(self) -> None:
        self.load_program(self.current_program)

    @Slot()
    def load_program(self, program: str | Program) -> None:
        if isinstance(program, str):
            print(f"Loading new program {os.path.basename(program)}")
            self.current_program = assemble(program)
        elif self.current_program is None:
            print(f"Loading new program {os.path.basename(program.filepath)}")
            self.current_program = program
        else:
            print(f"Reloading {os.path.basename(self.current_program.filepath)}")
        try:
            self.cpu.load_program(self.current_program)
            self.pixel_display.reset()
            self.keyboard.reset()
            self.text_display.reset()
        except SimulatorError as err:
            err.set_meta(self.current_meta)
            err.add_note("While loading the program", prepend=True)
            raise err
        # event = LoadProgramEvent(self.current_program)
        # GUI_APPLICATION.postEvent(self.cpu, event)
        # GUI_APPLICATION.postEvent(self.pixel_display, event)
        # GUI_APPLICATION.postEvent(self.keyboard, event)
        # GUI_APPLICATION.postEvent(self.text_display, event)

    def run(self, program: str | Program | None = None) -> NoReturn:
        print(f"Launching simulator in new window")
        self.show()
        if program is not None:
            program = assemble(program) if isinstance(program, str) else program
            self.load_program(program)
        app = QApplication.instance()
        if app is None:
            raise SimulatorError("Application not created yet")
        sys.exit(app.exec())
