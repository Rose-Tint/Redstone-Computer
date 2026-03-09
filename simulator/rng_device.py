from random import randint
from .io_ports import Port, Slot


class RNGDevice:
    def __init__(self, port: Port):
        self.buffer: str = ""
        self.port: Port = port
        self.port.input_read.connect(self.generate)

    @Slot()
    def generate(self) -> None:
        self.port.write_input(randint(0, 255))
