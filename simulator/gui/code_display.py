# from .common import *
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QTextEdit
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QTextDocument, QTextCursor, QTextBlockFormat, QColor
from assembler import Program, ast
from ..common import Reloadable

class CodeDisplay(QTextEdit, Reloadable):
    HIGHLIGHT_BG_COLOR = QColor.fromRgba64(240, 91, 137)
    MIMETYPE = "text/plain"
    file_dropped = Signal(str)

    def __init__(self, parent: QWidget):
        super().__init__(parent, readOnly=True)
        self.doc: QTextDocument = QTextDocument(self)
        self.doc.setDefaultFont("Consolas")
        self.setDocument(self.doc)
        self.setMinimumWidth(350)
        self.setAcceptDrops(True)

    def highlight(self, addr: int):
        if self.doc.isUndoAvailable():
            self.doc.undo()
        block = self.doc.findBlockByLineNumber(addr - 1)
        cursor = QTextCursor(block)
        cursor.setVisualNavigation(True)
        cursor.beginEditBlock()
        format: QTextBlockFormat = cursor.blockFormat()
        format.setBackground(self.HIGHLIGHT_BG_COLOR)
        cursor.setBlockFormat(format)
        cursor.endEditBlock()

    def reset(self) -> None:
        self.doc: QTextDocument = QTextDocument(self)
        self.doc.setDefaultFont("Consolas")
        self.setDocument(self.doc)

    def load_program(self, program: Program) -> None:
        lines: list[str] = []
        for addr, instruction in enumerate(program.code, 1):
            line = f"{addr:>4} | {repr(instruction)}"
            lines.append(line)
        text: str = "\n".join(lines)
        self.doc: QTextDocument = QTextDocument(text, self)
        self.doc.setDefaultFont("Consolas")
        self.setDocument(self.doc)

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

