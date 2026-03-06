from typing import TypeAlias
import abc
from assembler import Program
from PySide6.QtCore import QEvent, QObject
from PySide6.QtWidgets import QWidget


Word: TypeAlias = int

Addr: TypeAlias = int

class ResetEvent(QEvent):
    def __init__(self):
        super().__init__(QEvent.Type.User)

class LoadProgramEvent(QEvent):
    def __init__(self, program: Program):
        super().__init__(QEvent.Type.User)
        self.program = program

class Reloadable:
    def __init_subclass__(cls) -> None:
        def event(self, event: QEvent) -> bool:
            if isinstance(event, ResetEvent):
                self.reset()
                return True
            elif isinstance(event, LoadProgramEvent):
                self.load_program(event.program)
                return True
            else:
                return super(self.__class__, self).event(event)
        if issubclass(cls, QWidget):
            cls.event = event

    def reset(self) -> None:
        return

    def load_program(self, program: Program) -> None:
        self.reset()

class InterpreterError(Exception):
    pass

class UnexpectedEndOfInstrMem(InterpreterError):
    def __init__(self, msg: str = ""):
        super().__init__("Unexpectedly reached end of instruction memory " + msg)

def bounds_check(n: Word) -> Word:
    if -128 > n or n > 255:
        raise InterpreterError(f"word out of bounds ({n})")
    else:
        return n

def clamp(min: int, max: int, x: int) -> int:
    if x < min: x = min
    if x > max: x = max
    return x

def clamp_word(n: Word) -> Word:
    return clamp(-127, 255, n)
