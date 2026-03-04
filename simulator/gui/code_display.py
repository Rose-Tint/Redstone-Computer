# from .common import *
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QTextEdit
from PySide6.QtGui import QTextDocument, QTextCursor, QTextBlockFormat
from assembler import ast


class CodeDisplay(QTextEdit):
    HIGHLIGHT_BG_COLOR = QColor.fromRgba64(240, 91, 137)

    def __init__(self, parent: QWidget, code: ast.ResolvedCode):
        super().__init__(parent, readOnly=True)
        lines: list[str] = []
        for addr, instruction in enumerate(code, 1):
            line = f"{addr:>4} | {repr(instruction)}"
            lines.append(line)
        text: str = "\n".join(lines)
        self.doc: QTextDocument = QTextDocument(text, self)
        self.doc.setDefaultFont("Consolas")
        self.doc.setPlainText(text)
        self.setDocument(self.doc)
        self.setMinimumWidth(350)


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

