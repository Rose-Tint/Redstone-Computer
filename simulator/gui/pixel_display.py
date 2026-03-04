from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QGridLayout, QSizePolicy
from PySide6.QtGui import QMouseEvent, QPixmap


class Pixel(QLabel):
    PX_WIDTH = PX_HEIGHT = 6

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.is_on: bool = False
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFixedSize(self.PX_WIDTH, self.PX_HEIGHT)
        # self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        # self.resize(self.PX_WIDTH, self.PX_HEIGHT)
        self.adjustSize()
        self.off()

    def on(self) -> None:
        texture = QPixmap("gui/assets/redstone_lamp_on.png")
        self.setPixmap(texture.scaled(self.size()))
        self.is_on = True

    def off(self) -> None:
        texture = QPixmap("gui/assets/redstone_lamp_off.png")
        self.setPixmap(texture.scaled(self.size()))
        self.is_on = False

class PixelDisplay(QWidget):
    MAX_WIDTH = MAX_HEIGHT = 63

    def __init__(self, parent: QWidget | None):
        super().__init__(parent)
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
