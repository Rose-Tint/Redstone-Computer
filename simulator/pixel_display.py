from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QWidget, QLabel, QGridLayout, QSizePolicy
from PySide6.QtGui import QPixmap
from .io_ports import Port
from .common import Reloadable


class Pixel(QLabel):
    PX_WIDTH = PX_HEIGHT = 6

    def __init__(self, parent: "PixelDisplay"):
        super().__init__(parent)
        self.is_on: bool = False
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFixedSize(self.PX_WIDTH, self.PX_HEIGHT)
        # self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        # self.resize(self.PX_WIDTH, self.PX_HEIGHT)
        self.adjustSize()
        self.off()

    def on(self) -> None:
        texture = QPixmap("simulator/assets/redstone_lamp_on.png")
        self.setPixmap(texture.scaled(self.size()))
        self.is_on = True

    def off(self) -> None:
        texture = QPixmap("simulator/assets/redstone_lamp_off.png")
        self.setPixmap(texture.scaled(self.size()))
        self.is_on = False

class PixelDisplay(QWidget, Reloadable):
    MAX_WIDTH = MAX_HEIGHT = 63

    def __init__(self, parent: QWidget, op_p: Port, x1_p: Port, y1_p: Port, x2_p: Port, y2_p: Port):
        super().__init__(parent)
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
        self.pixels: list[list[Pixel]] = []
        grid = QGridLayout(self)
        grid.setSpacing(0)
        for x in range(self.MAX_WIDTH + 1):
            column: list[Pixel] = []
            for y in range(self.MAX_HEIGHT + 1):
                pixel = Pixel(self)
                column.append(pixel)
                grid.addWidget(pixel, x, y)
            self.pixels.append(column)
        grid.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(grid)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    @Slot()
    def op_slot(self, _value: int) -> None:
        if self.x2_arg == 0 or self.y2_arg == 0:
            self.draw_pixel(self.x1_arg-1, self.y1_arg-1)
        else:
            self.draw_square(self.x1_arg-1, self.y1_arg-1, self.x2_arg-1, self.y2_arg-1)
        self.x1_arg = 0
        self.y1_arg = 0
        self.x2_arg = 0
        self.y2_arg = 0

    @Slot(int)
    def x1_slot(self, value: int) -> None:
        self.x1_arg = value

    @Slot(int)
    def y1_slot(self, value: int) -> None:
        self.y1_arg = value

    @Slot(int)
    def x2_slot(self, value: int) -> None:
        self.x2_arg = value

    @Slot(int)
    def y2_slot(self, value: int) -> None:
        self.y2_arg = value

    def draw_pixel(self, x: int, y: int) -> None:
        if x > self.MAX_WIDTH or y > self.MAX_HEIGHT:
            raise IndexError(f"Error: coordinates ({x}, {y}) out of range")
        self.pixels[x][y].on()

    def draw_square(self, x1: int, y1: int, x2: int, y2: int) -> None:
        # mc cpu display requires that x1 < x2 and y1 > y2
        for x in range(x1, x2):
            for y in range(y2, y1):
                self.draw_pixel(x, y)

    def clear(self) -> None:
        for column in self.pixels:
            for pixel in column:
                pixel.off()

    def reset(self) -> None:
        for pxs in self.pixels:
            for px in pxs:
                px.off()
