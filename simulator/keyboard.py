from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton, QLineEdit, QSizePolicy
from utils import Queue
from .io_ports import Port
from .common import Reloadable


class Keyboard(QWidget, Reloadable):
    ENTER: str = "\n"
    RESET: str = "\x18"
    BACKSPACE: str = "\x08"
    TOP_ROW: str = "!?:\"%^/•()-+" + BACKSPACE
    SND_ROW: str = "1234567890="
    MID_ROW: str = "QWERTYUIOP"
    LWR_ROW: str = "ASDFGHJKL" + ENTER
    BTM_ROW: str = "ZXCVBNM,." + RESET
    SPACE: str = " "
    CONTROL_CHARS: str = ENTER + RESET + BACKSPACE
    ACCEPTED_CHARACTERS: str = TOP_ROW + SND_ROW + MID_ROW + LWR_ROW + BTM_ROW + SPACE

    key_pressed = Signal(str)

    def __init__(self, parent: QWidget, status_p: Port, buffer_p: Port):
        super().__init__(parent)
        self.submitted = False
        self.queue: Queue[int] = Queue()
        self.status_port = status_p
        self.buffer_port = buffer_p
        self.status_port.input_read.connect(self.update_status)
        self.buffer_port.input_read.connect(self.pop_buffer)
        self.submitted: bool = False
        self.buttons: dict[str, QPushButton] = {}
        self.text_widget = QLineEdit(self, maxLength=32, readOnly=True)
        grid = QGridLayout(self)
        grid.addWidget(self.text_widget, 0, 0, 1, -1)
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

    @Slot()
    def update_status(self) -> None:
        status = len(self.queue) | (int(self.submitted) << 7)
        self.status_port.write_input(status)

    @Slot()
    def pop_buffer(self) -> None:
        if self.queue.empty():
            self.buffer_port.write_input(0)
        elif (key := self.queue.pop()) is not None:
            self.buffer_port.write_input(key)
        self.update_status()

    def _make_button(self, key: str) -> QPushButton:
        label: str = ""
        shortcut = None
        min_width: int = 40
        match key:
            case self.ENTER:
                label = "Enter"
                shortcut = Qt.Key.Key_Enter
                min_width = 60
            case self.RESET:
                label = "Reset"
                shortcut = Qt.Key.Key_Escape # maybe not?
                min_width = 60
            case self.BACKSPACE:
                label = "Backspace"
                shortcut = Qt.Key.Key_Backspace
                min_width = 80
            case self.SPACE:
                label = "Space"
                shortcut = Qt.Key.Key_Space
                min_width = 60
            case _:
                label = key
                shortcut = key
        button = QPushButton(label, self, flat=False)
        button.setShortcut(shortcut)
        button.setMinimumSize(min_width, 30)
        button.adjustSize()
        button.clicked.connect(self.mk_key_slot(key))
        self.buttons[key] = button
        return button

    def mk_key_slot(self, key: str) -> Slot:
        @Slot()
        def slot():
            if len(self.queue) >= 32:
                return
            else:
                match key:
                    case self.ENTER:
                        self.submitted = True
                    case self.RESET:
                        self.queue.clear()
                    case self.BACKSPACE:
                        self.queue.pop()
                    case _:
                        self.queue.push(ord(key))
                self.update_display()
        return slot

    def update_display(self) -> None:
        text = ""
        for n in reversed(self.queue.data):
            if (ch := chr(n)) not in self.CONTROL_CHARS:
                text += ch
        self.text_widget.setText(text)

    def reset(self) -> None:
        self.submitted = False
        self.queue.clear()
        self.update_display()
