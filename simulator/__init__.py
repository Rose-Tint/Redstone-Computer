from asyncio import sleep
from threading import Thread
from assembler import Program
from PySide6.QtWidgets import QWidget, QMainWindow, QToolBar
from PySide6.QtGui import QAction
from .gui import launch_gui, MainGUI
from .gui.control import RunState
from .common import *
from .cpu import CPU
from .io_ports import *
from .inputs import *
from .inputs.pixel_display import *


# class Simulator(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.gui = MainGUI()
#         self.cpu = CPU(self.gui)
#         self.setCentralWidget(self.gui)

def run_simulator(path: str, program: Program) -> None:
    gui = MainGUI()
    cpu = CPU(gui)
    keyboard = Keyboard(gui.keyboard, cpu.ports[6], cpu.ports[7])
    text_display = TextDisplay(gui.text_display, cpu.ports[8], cpu.ports[9])
    pixel_display = PixelDisplay(gui.pixel_display, cpu.ports[1], cpu.ports[2], cpu.ports[3], cpu.ports[4], cpu.ports[5])
    rng = RNG(cpu.ports[10])
    gui.load_program(path, program)
    launch_gui(gui)
