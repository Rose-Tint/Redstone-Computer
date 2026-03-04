from ..common import *
from assembler import ast
import gui


class RegisterFile:
    def __init__(self, widget: gui.RegisterFile) -> None:
        self.widget = widget
        self.registers: list[Word] = [0] * 8

    def __setitem__(self, register: ast.Register, value: Word):
        regn = register.value
        if regn == 0:
            raise InterpreterError("tried to set register 0")
        elif regn > 7 or regn < 0:
            raise InterpreterError(f"invalid register {regn}")
        else:
            value = clamp_word(value)
            self.registers[regn] = value
            self.widget.write(regn, value)

    def __getitem__(self, register: ast.Register) -> Word:
        regn = register.value
        if regn > 7 or regn < 0:
            raise InterpreterError(f"invalid register {regn}")
        else:
            return self.registers[regn]


