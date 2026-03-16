from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QTextEdit
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QTextDocument, QTextCursor, QTextBlockFormat, QColor
from assembler import Program, ast
from utils import Stack
from .common import Reloadable, Addr
from .error import EndOfInstrMem, InstrAddrOutOfRange, CallStackOverflow, CallStackEmpty, ProgramTooBig

class InstructionMemory(QTextEdit, Reloadable):
    HIGHLIGHT_BG_COLOR = QColor.fromRgba64(240, 91, 137)
    MIMETYPE = "text/plain"
    MAX_SIZE: int = 1024

    file_dropped = Signal(str)

    def __init__(self, parent: QWidget):
        super().__init__(parent, readOnly=True)
        self.instructions = [ast.NOOP] * self.MAX_SIZE
        self.call_stack: Stack = Stack()
        self.pc: Addr = 0
        self.setDocument(QTextDocument(self))
        self.document().setDefaultFont("Consolas")
        self.setMinimumWidth(350)
        self.setAcceptDrops(True)

    def jump(self, addr: Addr) -> None:
        if addr >= self.MAX_SIZE:
            raise InstrAddrOutOfRange(addr, self.MAX_SIZE)
        self.pc = addr

    def push_cs_and_jump(self, addr: Addr):
        if len(self.call_stack) > 16:
            raise CallStackOverflow()
        self.call_stack.push(self.pc)
        self.jump(addr)

    def pop_cs_and_jump(self):
        if self.call_stack.empty():
            raise CallStackEmpty()
        addr = self.call_stack.pop()
        self.jump(addr)

    def advance(self) -> ast.Instruction:
        if self.pc >= len(self.instructions):
            raise EndOfInstrMem(self.pc)
        ins = self.instructions[self.pc]
        self.pc += 1
        self.highlight(self.pc)
        return ins

    def highlight(self, addr: int | None = None):
        addr = addr or self.pc
        if self.document().isUndoAvailable():
            self.document().undo()
        block = self.document().findBlockByLineNumber(addr - 1)
        cursor = QTextCursor(block)
        cursor.setVisualNavigation(True)
        cursor.beginEditBlock()
        format: QTextBlockFormat = cursor.blockFormat()
        format.setBackground(self.HIGHLIGHT_BG_COLOR)
        cursor.setBlockFormat(format)
        cursor.endEditBlock()
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

    def reset(self) -> None:
        self.document().setPlainText("")

    def load_program(self, program: Program) -> None:
        if (size := len(program.code)) > self.MAX_SIZE:
            raise ProgramTooBig(size, self.MAX_SIZE)
        self.instructions = program.code
        lines: list[str] = []
        for addr, instruction in enumerate(program.code, 1):
            line = f"{addr:>4} | {repr(instruction)}"
            lines.append(line)
        self.document().setPlainText("\n".join(lines))

    def dragEnterEvent(self, e: QDragEnterEvent) -> None:
        if e.mimeData().hasFormat(self.MIMETYPE):
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e: QDropEvent) -> None:
        if e.mimeData().hasFormat(self.MIMETYPE):
            data = e.mimeData().data(self.MIMETYPE)
            self.file_dropped.emit(data)
            e.accept()
        else:
            e.ignore()

