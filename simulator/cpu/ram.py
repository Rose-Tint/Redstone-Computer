from ..common import *
import gui


class RAM:
    MAX_SIZE = 256
    def __init__(self, widget: gui.RAM) -> None:
        self.widget = widget
        self.ram: list[Word] = [0] * self.MAX_SIZE

    def load(self, ram: list[Word]) -> None:
        size = len(ram)
        if size > self.MAX_SIZE:
            raise InterpreterError(f"program too big: {size} (max is {self.MAX_SIZE})")
        while len(ram) < self.MAX_SIZE:
            ram.append(0)
        self.ram = ram
        self.widget.update_ram(self.ram)

    def __setitem__(self, addr: int, value: Word):
        if 0 > addr or addr >= self.MAX_SIZE:
            raise InterpreterError(f"invalid RAM address {addr}")
        else:
            value = clamp_word(value)
            self.ram[addr] = value
            self.widget.write(addr, value)

    def __getitem__(self, addr: int) -> Word:
        if 0 > addr or addr >= self.MAX_SIZE:
            raise InterpreterError(f"invalid RAM address {addr}")
        else:
            return self.ram[addr]

