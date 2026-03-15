from PySide6.QtCore import Qt, Signal, QTimer, Slot
from PySide6.QtWidgets import QWidget, QLabel, QGridLayout, QPushButton
from PySide6.QtWidgets import QSlider


class ExecutionRateSlider(QWidget):
    MAX_RATE = 100

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMaximum(self.MAX_RATE)
        self.slider.setMinimum(1)
        self.slider.setValue(self.MAX_RATE)
        self.slider.valueChanged.connect(self.update_main_label)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.main_label = QLabel(self.main_label_text(), self)
        grid = QGridLayout(self)
        grid.addWidget(self.main_label, 0, 0, 1, -1)
        grid.addWidget(QLabel("1", self), 1, 0)
        grid.addWidget(self.slider, 1, 1)
        grid.addWidget(QLabel(str(self.MAX_RATE), self), 1, 2)
        self.setLayout(grid)

    def update_main_label(self, _):
        self.main_label.setText(self.main_label_text())

    def main_label_text(self) -> str:
        rate = "MAX" if self.rate == self.MAX_RATE else str(self.rate)
        return f"Execution Rate: {rate:>4}/sec"

    @property
    def rate(self) -> int:
        return self.slider.value()

class ProgramControl(QWidget):
    step = Signal()
    reload_program = Signal()

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.paused: bool = True
        self.start_btn = QPushButton("Start", self, flat=True)
        self.start_btn.clicked.connect(self.start_stop)
        self.step_btn = QPushButton("Step", self, flat=True)
        self.step_btn.clicked.connect(self.step.emit)
        self.reload_btn = QPushButton("Reload", self, flat=True)
        self.reload_btn.clicked.connect(self.reload_program.emit)
        self.rate_slider = ExecutionRateSlider(self)
        self.rate_slider.slider.valueChanged.connect(self.set_exec_rate)
        grid = QGridLayout(self)
        grid.addWidget(self.start_btn, 0, 0)
        grid.addWidget(self.step_btn, 0, 1)
        grid.addWidget(self.reload_btn, 0, 2)
        grid.addWidget(self.rate_slider, 1, 0, 1, -1)
        self.setLayout(grid)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.execute)
        self.timer.start(ExecutionRateSlider.MAX_RATE // self.rate)

    def pause(self) -> None:
            self.start_btn.setText("Resume")
            self.paused = True

    def resume(self) -> None:
            self.start_btn.setText("Pause")
            self.paused = False

    @Slot()
    def start_stop(self) -> None:
        if self.paused: # currently paused, need to resume
             self.resume()
        else: # currently running, need to pause
            self.pause()

    @Slot()
    def reload(self) -> None:
        self.pause()
        self.reload_program.emit()

    @Slot()
    def execute(self) -> None:
        if not self.paused:
            self.step.emit()

    @Slot()
    def set_exec_rate(self, value: int) -> None:
        self.timer.setInterval(1000 // value)

    @property
    def rate(self) -> int:
        return self.rate_slider.rate
