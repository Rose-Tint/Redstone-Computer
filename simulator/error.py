import os.path
from assembler import ast


class SimulatorError(Exception):
    def __init__(self, title: str, msg: str|None=None):
        super().__init__()
        self.title: str = title
        self.title_msg: str | None = msg
        self.meta: ast.Meta = ast.Meta.mk_intrinsic()
        self.file: str | None = None
        self.line: int | None = None
        self._notes: list[str] = []

    def set_meta(self, meta: ast.Meta) -> None:
        self.meta = meta

    def add_note(self, msg: str, prepend: bool = False):
        if prepend:
            self._notes.insert(0, msg)
        else:
            self._notes.append(msg)
        return self

    def __str__(self) -> str:
        # header
        msg = "\nSimulator Error"
        if self.file is not None:
            msg += f" in {os.path.abspath(self.file)}"
        if self.line is not None:
            msg += f" on line {self.file}"
        # title
        msg += f"\n{self.title}"
        if self.title_msg is not None:
            msg += f": {self.title_msg}"
        # notes
        for note in self._notes:
            note = note.replace("\n", "\n\t")
            msg += f"\n\t{note}"
        return msg + "\n"

class InvalidInstruction(SimulatorError):
    def __init__(self, instr: ast.Instruction | None = None):
        super().__init__(f"Invalid Instruction", repr(instr) if instr is not None else None)
        self.instruction = instr

    def set_instruction(self, instr: ast.Instruction) -> "InvalidInstruction":
        self.instruction = instr
        self.title = f"Invalid Instruction: {instr}"
        return self

class InvalidRegister(InvalidInstruction):
    def __init__(self, register: ast.Register | int):
        super().__init__()
        if isinstance(register, int):
            register = ast.Register.from_int(register)
        self.add_note(f"Register {register} does not exist")

class InvalidPort(InvalidInstruction):
    def __init__(self, port: int | ast.Define):
        super().__init__()
        self.add_note(f"Port {port} does not exist")

class InvalidRAMAddress(SimulatorError):
    def __init__(self, addr: int):
        super().__init__("Invalid RAM address", str(addr))

class InstrAddrOutOfRange(InvalidInstruction):
    def __init__(self, addr: int, max_size: int):
        super().__init__()
        self.add_note(f"Tried to jump/branch to address out of range")
        self.add_note(f"Address was {addr} but max is {max_size - 1}")

class EndOfInstrMem(SimulatorError):
    def __init__(self, addr: int):
        super().__init__("Unexpected End of Instructions")
        self.add_note(f"Attempted to advance to next instruction at address {addr}")

class CallStackOverflow(SimulatorError):
    def __init__(self):
        super().__init__("Call Stack Overflow")

class CallStackEmpty(SimulatorError):
    def __init__(self):
        super().__init__("Call Stack Empty")
        self.add_note("Tried to pop from call stack while empty")

class VarStackOverflow(SimulatorError):
    def __init__(self):
        super().__init__("Call Stack Overflow")

class VarStackEmpty(SimulatorError):
    def __init__(self):
        super().__init__("Call Stack Empty")
        self.add_note("Tried to pop from var stack while empty")

class ProgramTooBig(SimulatorError):
    def __init__(self, size: int, max_size: int):
        super().__init__(f"Program Too Big")
        self.add_note(f"Program was {size} but max is {max_size}")
