from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QWidget
from assembler import Program, ast
from assembler.opcode import Opcode
from assembler.ast import Instruction, RegEncoded, ImmEncoded, JumpEncoded, SpecEncoded
from .instruction_memory import InstructionMemory
from .register_file import RegisterFile
from .ram import RAM
from .alu_flags import FlagsWidget, ALUFlags
from utils import Stack
from .common import Word, Reloadable
from .io_ports import IOPorts
from .error import SimulatorError, EndOfInstrMem, InvalidInstruction, VarStackOverflow, VarStackEmpty


class CPU(QObject, Reloadable):
    meta_update = Signal(ast.Meta)

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
        try:
            self.instructions.reset()
            self.registers.reset()
            self.ram.reset()
            self.flags_widget.reset()
        except SimulatorError as err:
            err.add_note("While resetting CPU")
            raise err
        self.var_stack.clear()
        self.finished = False

    def load_program(self, program: Program) -> None:
        self.reset()
        self.instructions.load_program(program)
        self.ram.load_program(program)

    def step(self) -> None:
        if self.finished:
            return
        instruction = None
        try:
            instruction = self.instructions.advance()
            self.meta_update.emit(instruction.meta)
            self.execute(instruction)
        except InvalidInstruction as err:
            if instruction is not None:
                err.set_instruction(instruction)
            raise
        except EndOfInstrMem:
            self.finished = True
            raise

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
            raise InvalidInstruction(instr)

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
                self.registers.write(rt, int(imm))
            case Opcode.CMPI:
                self.set_flags(self.registers.read(rs) - int(imm))
            case Opcode.ADDI:
                self.registers.write(rt, self.set_flags(self.registers.read(rs) + int(imm)))
            case Opcode.SUBI:
                self.registers.write(rt, self.set_flags(self.registers.read(rs) - int(imm)))

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
                    raise VarStackOverflow()
                self.var_stack.push(self.registers.read(rs))
            case Opcode.POP:
                if len(self.var_stack) <= 0:
                    raise VarStackEmpty()
                self.registers.write(rs, self.var_stack.pop())
            case Opcode.EXIT:
                self.finished = True
