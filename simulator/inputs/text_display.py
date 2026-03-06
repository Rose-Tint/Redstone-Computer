from .. import gui
from ..io_ports import Port, Slot


class TextDisplay:
    def __init__(self, widget: gui.TextDisplay, buffer_port: Port, control_port: Port):
        self.widget = widget
        self._buffer: str = ""
        self.buffer_port: Port = buffer_port
        self.control_port: Port = control_port
        self.buffer_port.output_written.connect(self.push_character)
        self.control_port.output_written.connect(self.push_buffer)
        self.control_port.input_read.connect(self.clear_buffer)

    @property
    def buffer(self) -> str:
        return self._buffer

    @buffer.setter
    def buffer(self, new: str):
        self._buffer = new
        self.widget.buffer.setText(self.buffer)

    @Slot()
    def push_character(self, value: int) -> None:
        self.buffer += chr(value)

    @Slot()
    def push_buffer(self, _value: int) -> None:
        self.widget.display.setText(self.buffer)
        self.buffer = ""

    @Slot()
    def clear_buffer(self) -> None:
        self.buffer = ""
