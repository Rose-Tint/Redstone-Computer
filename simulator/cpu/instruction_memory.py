from assembler.ast.instructions import Instruction, NOOP
import gui
from utils import Stack
from ..common import *


class InstructionMemory:
    MAX_SIZE = 1024

    def __init__(self, widget: gui.CodeDisplay):
        self.widget = widget
        self.instructions: list[Instruction] = [NOOP] * self.MAX_SIZE
        self.call_stack: Stack = Stack()
        self._pc = 0

    @property
    def pc(self) -> int:
        return self._pc

    @pc.setter
    def pc(self, value: Addr) -> None:
        self._pc = value
        self.widget.highlight(self._pc)

    def jump(self, addr: Addr) -> None:
        if addr >= self.MAX_SIZE:
            raise InterpreterError(f"address {addr} out of {self.MAX_SIZE} range.")
        self.pc = addr

    def push_cs_and_jump(self, addr: Addr):
        print(f"DEBUG: pushing addr {addr} to [{', '.join(map(str, self.call_stack.data))}]", end="")
        if len(self.call_stack) > 16:
            raise InterpreterError("tried to push address but call stack full")
        self.call_stack.push(self.pc)
        print(f" -> [{', '.join(map(str, self.call_stack.data))}]")
        self.jump(addr)

    def pop_cs_and_jump(self):
        print(f"DEBUG: popping from [{', '.join(map(str, self.call_stack.data))}]", end="")
        if self.call_stack.empty():
            raise InterpreterError(f"tried to pop address but call stack empty (currently at addr {self.pc})")
        addr = self.call_stack.pop()
        print(f" -> [{', '.join(map(str, self.call_stack.data))}]")
        self.jump(addr)

    def advance(self) -> Instruction:
        ins = self.instructions[self.pc]
        self.pc += 1
        if self.pc >= self.MAX_SIZE:
            raise InterpreterError(f"reached end of memory")
        return ins

    def load(self, instructions: list[Instruction]) -> None:
        size = len(instructions)
        if size > self.MAX_SIZE:
            raise InterpreterError(f"program too big: {size} (max is {self.MAX_SIZE})")
        self.instructions = instructions
        # while len(instructions) < self.MAX_SIZE:
        #     self.instructions.append(NOOP)

