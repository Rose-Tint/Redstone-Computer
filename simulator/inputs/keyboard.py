from asyncio import Task, create_task
from utils import Queue
import gui
from ..io_ports import Port, Slot


class Keyboard:
    def __init__(self, widget: gui.Keyboard, status_port: Port, buffer_port: Port):
        self.widget = widget
        self.submitted = False
        self.queue: Queue = Queue()
        self.status_port = status_port
        self.buffer_port = buffer_port
        self.widget.key_pressed.connect(self.handle_key_press)
        self.status_port.input_read.connect(self.update_status)
        self.buffer_port.input_read.connect(self.pop_buffer)

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

    def handle_key_press(self, key: str):
        match key:
            case gui.Keyboard.ENTER:
                self.submitted = True
            case gui.Keyboard.RESET:
                self.queue.clear()
            case gui.Keyboard.BACKSPACE:
                self.queue.pop()
            case _:
                self.queue.push(ord(key))
