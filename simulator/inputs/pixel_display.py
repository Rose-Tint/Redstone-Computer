from asyncio import Task, create_task
from dataclasses import dataclass
import gui
from ..common import InterpreterError
from ..io_ports import Port, Slot


class PixelDisplay:
    def __init__(self, widget: gui.PixelDisplay, op_p: Port, x1_p, y1_p, x2_p, y2_p):
        self.widget = widget
        self.x1_arg: int = 0
        self.y1_arg: int = 0
        self.x2_arg: int = 0
        self.y2_arg: int = 0
        self.op_port: Port = op_p
        self.x1_port: Port = x1_p
        self.y1_port: Port = y1_p
        self.x2_port: Port = x2_p
        self.y2_port: Port = y2_p
        self.op_port.output_written.connect(self.op_slot)
        self.x1_port.output_written.connect(self.x1_slot)
        self.y1_port.output_written.connect(self.y1_slot)
        self.x2_port.output_written.connect(self.x2_slot)
        self.y2_port.output_written.connect(self.y2_slot)

    @Slot()
    def op_slot(self, _value: int) -> None:
        if self.x2_arg == 0 or self.y2_arg == 0:
            self.widget.draw_pixel(self.x1_arg-1, self.y1_arg-1)
        else:
            self.widget.draw_square(self.x1_arg-1, self.y1_arg-1, self.x2_arg-1, self.y2_arg-1)
        self.x1_arg = 0
        self.y1_arg = 0
        self.x2_arg = 0
        self.y2_arg = 0

    @Slot()
    def x1_slot(self, value: int) -> None:
        self.x1_arg = value

    @Slot()
    def y1_slot(self, value: int) -> None:
        self.y1_arg = value

    @Slot()
    def x2_slot(self, value: int) -> None:
        self.x2_arg = value

    @Slot()
    def y2_slot(self, value: int) -> None:
        self.y2_arg = value

