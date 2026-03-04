from PySide6.QtCore import Slot
from assembler.opcode import Opcode
from assembler.ast.instructions import RegEncoded
from assembler.ast.instructions import ImmEncoded
from assembler.ast.instructions import JumpEncoded
from assembler.ast.instructions import SpecEncoded
import gui
from ..io_ports import *
from .instruction_memory import *
from .ram import *
from .registers import *


class CPU:
    def __init__(self, gui: gui.MainGUI) -> None:
        self.gui = gui
        self.instructions: InstructionMemory = InstructionMemory(gui.code_display)
        self.regs: RegisterFile = RegisterFile(gui.registers)
        self.ram: RAM = RAM(gui.ram)
        self.ports: IOPorts = IOPorts()
        self.overflow_flag: bool = False
        self.negative_flag: bool = False
        self.zero_flag: bool = False
        self.var_stack: list[Word] = []
        self.finished = False
        self.gui.program_control.step.connect(self.step)

    @Slot()
    def step(self) -> None:
        if self.finished:
            return
        instruction = None
        try:
            instruction = self.instructions.advance()
            self.execute(instruction)
        except InterpreterError as err:
            if isinstance(err, UnexpectedEndOfInstrMem):
                self.finished = True
            pc = self.instructions.pc
            msg = f"Error while executing instruction {pc}"
            if instruction is not None:
                msg += f" ({repr(instruction)})"
            print(msg)
            err.__traceback__ = None
            raise err

    def set_flags(self, value: Word) -> Word:
        self.negative_flag = value < 0
        self.overflow_flag = value > 255
        self.zero_flag = value == 0
        self.gui.flags.set_flags(self.overflow_flag, self.negative_flag, self.zero_flag)
        return value

    def execute(self, instr: Instruction) -> None:
        # print(f"DEBUG: executing {repr(instr)}")
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
                self.regs[rd] = self.set_flags(self.regs[rs] + self.regs[rt])
            case Opcode.SUB:
                self.regs[rd] = self.set_flags(self.regs[rs] - self.regs[rt])
            case Opcode.CMP:
                self.set_flags(self.regs[rs] - self.regs[rt])
            case Opcode.AND:
                self.regs[rd] = self.set_flags(self.regs[rs] & self.regs[rt])
            case Opcode.OR:
                self.regs[rd] = self.set_flags(self.regs[rs] | self.regs[rt])
            case Opcode.XOR:
                self.regs[rd] = self.set_flags(self.regs[rs] ^ self.regs[rt])
            case Opcode.NOR:
                self.regs[rd] = self.set_flags(~(self.regs[rs] | self.regs[rt]))
            case _:
                raise InterpreterError(f"invalid register-encoded instruction {opcode}")

    def imm_encoded(self, opcode, rs, rt, imm):
        match opcode:
            case Opcode.SHL:
                self.regs[rt] = self.set_flags(self.regs[rs] << 1)
            case Opcode.SHR:
                self.regs[rt] = self.set_flags(self.regs[rs] >> 1)
            case Opcode.LW:
                # print("DEBUG: rt{%s} = [rs{%s}]{%s}" % (rt, rs, self.regs[rs]) )
                self.regs[rs] = self.ram[self.regs[rt]]
            case Opcode.SW:
                self.ram[self.regs[rt]] = self.regs[rs]
            case Opcode.LI:
                self.regs[rt] = imm
            case Opcode.CMPI:
                self.set_flags(self.regs[rs] - imm)
            case Opcode.ADDI:
                self.regs[rt] = self.set_flags(self.regs[rs] + imm)
            case Opcode.SUBI:
                self.regs[rt] = self.set_flags(self.regs[rs] - imm)
            case _:
                raise InterpreterError(f"invalid immediate-encoded instruction {opcode}")

    def jump_encoded(self, opcode, addr):
        match opcode:
            case Opcode.JUMP:
                self.instructions.jump(addr)
            case Opcode.CALL:
                self.instructions.push_cs_and_jump(addr)
            case Opcode.BRZ:
                if self.zero_flag:
                    self.instructions.jump(addr)
            case Opcode.BNZ:
                if not self.zero_flag:
                    self.instructions.jump(addr)
            case Opcode.BRO:
                if self.overflow_flag:
                    self.instructions.jump(addr)
            case Opcode.BNO:
                if not self.overflow_flag:
                    self.instructions.jump(addr)
            case Opcode.BRN:
                if self.negative_flag:
                    self.instructions.jump(addr)
            case Opcode.BNN:
                if not self.negative_flag:
                    self.instructions.jump(addr)
            case _:
                raise InterpreterError(f"invalid jump-encoded instruction {opcode}")

    def spec_encoded(self, opcode, rs, port, _imm):
        match opcode:
            case Opcode.RETURN:
                self.instructions.pop_cs_and_jump()
            case Opcode.RP:
                self.regs[rs] = self.ports[port].read_input()
            case Opcode.WP:
                self.ports[port].write_output(self.regs[rs])
            case Opcode.PUSH:
                if len(self.var_stack) > 16:
                    raise InterpreterError("tried to push to var stack while stack full")
                self.var_stack.insert(0, self.regs[rs])
            case Opcode.POP:
                if len(self.var_stack) <= 0:
                    raise InterpreterError("tried to push to var stack while stack full")
                self.regs[rs] = self.var_stack.pop()
            case Opcode.EXIT:
                self.finished = True
                print("DEBUG: Program finished!")
            case _:
                raise InterpreterError(f"invalid special-encoded instruction {opcode}")


