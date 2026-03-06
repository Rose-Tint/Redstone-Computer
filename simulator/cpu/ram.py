from ..common import *
from .. import gui
from ..common import Reloadable


class RAM(Reloadable):
    MAX_SIZE = 256
    def __init__(self, widget: gui.RAM) -> None:
        self.widget = widget
        self.ram: list[Word] = [0] * self.MAX_SIZE

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

    def reset(self) -> None:
        self.ram = [0] * self.MAX_SIZE

    def load_program(self, program: gui.Program) -> None:
        size = len(program.data)
        if size > self.MAX_SIZE:
            raise InterpreterError(f"program too big: {size} (max is {self.MAX_SIZE})")
        while len(program.data) < self.MAX_SIZE:
            program.data.append(0)
        self.ram = program.data
        self.widget.update_ram(self.ram)
