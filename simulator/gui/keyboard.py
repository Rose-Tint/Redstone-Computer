from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton, QLineEdit, QSizePolicy
from assembler import Program
from utils import Queue
from ..common import Reloadable


class Keyboard(QWidget, Reloadable):
    # TODO: is this up to date?
    ENTER = "\n"
    RESET = "\x18"
    BACKSPACE = "\x08"
    TOP_ROW = "!?:\"%^/•()-+" + BACKSPACE
    SND_ROW = "1234567890="
    MID_ROW = "QWERTYUIOP"
    LWR_ROW = "ASDFGHJKL" + ENTER
    BTM_ROW = "ZXCVBNM,." + RESET
    SPACE = " "
    CONTROL_CHARS = ENTER + RESET + BACKSPACE
    ACCEPTED_CHARACTERS = TOP_ROW + SND_ROW + MID_ROW + LWR_ROW + BTM_ROW + SPACE

    key_pressed = Signal(str)

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.buffer: Queue[int] = Queue()
        self.submitted: bool = False
        self.buttons: dict[str, QPushButton] = {}
        self.text = QLineEdit(self, maxLength=32, readOnly=True)
        grid = QGridLayout(self)
        grid.addWidget(self.text, 0, 0, 1, -1)
        def make_row(row: int, keys: str):
            for i, key in enumerate(keys):
                button = self._make_button(key)
                grid.addWidget(button, row, 2*i + row, 1, 2)
        make_row(1, self.TOP_ROW)
        make_row(2, self.SND_ROW)
        make_row(3, self.MID_ROW)
        make_row(4, self.LWR_ROW)
        make_row(5, self.BTM_ROW)
        space_btn = self._make_button(self.SPACE)
        grid.addWidget(space_btn, 6, 0, 1, -1)
        grid.setSpacing(2)
        grid.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.setLayout(grid)
        self.resize(60, 40)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)

    def _make_button(self, key: str) -> QPushButton:
        label: str = ""
        min_width: int = 40
        match key:
            case self.ENTER:
                label = "Enter"
                min_width = 60
            case self.RESET:
                label = "Reset"
                min_width = 60
            case self.BACKSPACE:
                label = "Backspace"
                min_width = 80
            case self.SPACE:
                label = "Space"
                min_width = 60
            case _:
                label = key
        button = QPushButton(label, self, flat=False)
        button.setShortcut(key)
        button.setMinimumSize(min_width, 30)
        button.adjustSize()
        button.clicked.connect(self.mk_key_slot(key))
        self.buttons[key] = button
        return button

    def mk_key_slot(self, key: str) -> Slot:
        @Slot()
        def slot():
            if len(self.buffer) >= 32:
                return
            else:
                self.key_pressed.emit(key)
                match key:
                    case self.ENTER:
                        self.submitted = True
                    case self.RESET:
                        self.buffer.clear()
                    case self.BACKSPACE:
                        self.buffer.pop()
                    case _:
                        self.buffer.push(ord(key))
                self.update_display()
        return slot

    def update_display(self) -> None:
        text = ""
        for n in reversed(self.buffer.data):
            if (ch := chr(n)) not in self.CONTROL_CHARS:
                text += ch
        self.text.setText(text)

    def reset(self) -> None:
        self.submitted = False
        self.buffer.clear()
        self.update_display()
