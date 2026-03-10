from PySide6.QtCore import Slot
from assembler.opcode import Opcode
from assembler.ast import Instruction, RegEncoded, ImmEncoded, JumpEncoded, SpecEncoded
from .instruction_memory import InstructionMemory
from .register_file import RegisterFile
from .ram import RAM
from .alu_flags import FlagsWidget, ALUFlags
from utils import Stack
from .io_ports import *


class CPU(QObject, Reloadable):
    # finished = Signal(bool)

    def __init__(self, parent: QWidget, ports: IOPorts) -> None:
        super().__init__(parent)
        self.instructions: InstructionMemory = InstructionMemory(parent)
        self.registers: RegisterFile = RegisterFile(parent)
        self.ram: RAM = RAM(parent)
        self.flags_widget = FlagsWidget(parent)
        self.ports = ports
        self.var_stack: Stack = Stack()
        self.finished: bool = False

    def reset(self) -> None:
        self.instructions.reset()
        self.registers.reset()
        self.ram.reset()
        self.flags_widget.reset()
        self.var_stack.clear()
        self.finished = False

    def load_program(self, program: Program) -> None:
        self.reset()
        self.instructions.load_program(program)
        self.ram.load_program(program)

    @Slot()
    def step(self) -> None:
        if self.finished:
            return
        instruction = None
        try:
            instruction = self.instructions.advance()
            self.execute(instruction)
        except InterpreterError as err:
            if isinstance(err, EndOfInstrMemError):
                self.finished = True
            pc = self.instructions.pc
            msg = f"Error while executing instruction {pc}"
            if instruction is not None:
                msg += f" ({repr(instruction)})"
            print(msg)
            err.__traceback__ = None
            raise err

    @property
    def alu_flags(self) -> ALUFlags:
        return self.flags_widget.alu_flags

    def set_flags(self, value: Word) -> Word:
        self.flags_widget.alu_flags = ALUFlags.cmp(value)
        return value

    def execute(self, instr: Instruction) -> None:
        if isinstance(instr, RegEncoded):
            self.reg_encoded(instr.opcode, instr.rs, instr.rt, instr.rd)
        elif isinstance(instr, ImmEncoded):
            self.imm_encoded(instr.opcode, instr.rs, instr.rt, instr.imm)
        elif isinstance(instr, JumpEncoded):
            self.jump_encoded(instr.opcode, instr.addr)
        elif isinstance(instr, SpecEncoded):
            self.spec_encoded(instr.opcode, instr.rs, instr.port, instr.imm)
        else:
            raise InterpreterError(f"invalid instruction encoding for {repr(instr)}")

    def reg_encoded(self, opcode, rs, rt, rd):
        match opcode:
            case Opcode.NOOP:
                pass
            case Opcode.ADD:
                self.registers.write(rd, self.set_flags(self.registers.read(rs) + self.registers.read(rt)))
            case Opcode.SUB:
                self.registers.write(rd, self.set_flags(self.registers.read(rs) - self.registers.read(rt)))
            case Opcode.CMP:
                self.set_flags(self.registers.read(rs) - self.registers.read(rt))
            case Opcode.AND:
                self.registers.write(rd, self.set_flags(self.registers.read(rs) & self.registers.read(rt)))
            case Opcode.OR:
                self.registers.write(rd, self.set_flags(self.registers.read(rs) | self.registers.read(rt)))
            case Opcode.XOR:
                self.registers.write(rd, self.set_flags(self.registers.read(rs) ^ self.registers.read(rt)))
            case Opcode.NOR:
                self.registers.write(rd, self.set_flags(~(self.registers.read(rs) | self.registers.read(rt))))
            case _:
                raise InterpreterError(f"invalid register-encoded instruction {opcode}")

    def imm_encoded(self, opcode, rs, rt, imm):
        match opcode:
            case Opcode.SHL:
                self.registers.write(rt, self.set_flags(self.registers.read(rs) << 1))
            case Opcode.SHR:
                self.registers.write(rt, self.set_flags(self.registers.read(rs) >> 1))
            case Opcode.LW:
                self.registers.write(rs, self.ram.read(self.registers.read(rt)))
            case Opcode.SW:
                self.ram.write(self.registers.read(rt), self.registers.read(rs))
            case Opcode.LI:
                self.registers.write(rt, imm)
            case Opcode.CMPI:
                self.set_flags(self.registers.read(rs) - imm)
            case Opcode.ADDI:
                self.registers.write(rt, self.set_flags(self.registers.read(rs) + imm))
            case Opcode.SUBI:
                self.registers.write(rt, self.set_flags(self.registers.read(rs) - imm))
            case _:
                raise InterpreterError(f"invalid immediate-encoded instruction {opcode}")

    def jump_encoded(self, opcode, addr):
        match opcode:
            case Opcode.JUMP:
                self.instructions.jump(addr)
            case Opcode.CALL:
                self.instructions.push_cs_and_jump(addr)
            case Opcode.BRZ:
                if ALUFlags.Zero in self.alu_flags:
                    self.instructions.jump(addr)
            case Opcode.BNZ:
                if ALUFlags.Zero not in self.alu_flags:
                    self.instructions.jump(addr)
            case Opcode.BRO:
                if ALUFlags.Overflow in self.alu_flags:
                    self.instructions.jump(addr)
            case Opcode.BNO:
                if ALUFlags.Overflow not in self.alu_flags:
                    self.instructions.jump(addr)
            case Opcode.BRN:
                if ALUFlags.Negative in self.alu_flags:
                    self.instructions.jump(addr)
            case Opcode.BNN:
                if ALUFlags.Negative not in self.alu_flags:
                    self.instructions.jump(addr)
            case _:
                raise InterpreterError(f"invalid jump-encoded instruction {opcode}")

    def spec_encoded(self, opcode, rs, port, _imm):
        match opcode:
            case Opcode.RETURN:
                self.instructions.pop_cs_and_jump()
            case Opcode.RP:
                self.registers.write(rs, self.ports[port].read_input())
            case Opcode.WP:
                self.ports[port].write_output(self.registers.read(rs))
            case Opcode.PUSH:
                if len(self.var_stack) > 16:
                    raise InterpreterError("tried to push to var stack while stack full")
                self.var_stack.push(self.registers.read(rs))
            case Opcode.POP:
                if len(self.var_stack) <= 0:
                    raise InterpreterError("tried to push to var stack while stack full")
                self.registers.write(rs, self.var_stack.pop())
            case Opcode.EXIT:
                self.finished = True
                print("Program finished")
            case _:
                raise InterpreterError(f"invalid special-encoded instruction {opcode}")
