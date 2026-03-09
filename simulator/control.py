from enum import Enum
from PySide6.QtCore import Qt, Signal, QTimer, Slot
from PySide6.QtWidgets import QWidget, QLabel, QGridLayout, QPushButton
from PySide6.QtWidgets import QSlider


class RunState(Enum):
    PAUSED = 0
    RUNNING = 1

class ExecutionRateSlider(QWidget):
    MAX_RATE = 100

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMaximum(self.MAX_RATE)
        self.slider.setMinimum(1)
        self.slider.setValue(self.MAX_RATE)
        self.slider.valueChanged.connect(self.update_main_label)
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

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.run_state = RunState.PAUSED
        self.start_btn = QPushButton("Start", self, flat=True)
        self.start_btn.clicked.connect(lambda _: self.set_state(RunState.RUNNING))
        self.pause_btn = QPushButton("Pause", self, flat=True)
        self.pause_btn.clicked.connect(lambda _: self.set_state(RunState.PAUSED))
        self.step_btn = QPushButton("Step", self, flat=True)
        self.step_btn.clicked.connect(lambda _: self.step.emit())
        self.rate_slider = ExecutionRateSlider(self)
        self.rate_slider.slider.valueChanged.connect(self.set_exec_rate)
        grid = QGridLayout(self)
        grid.addWidget(self.start_btn, 0, 0)
        grid.addWidget(self.pause_btn, 0, 1)
        grid.addWidget(self.step_btn, 0, 2)
        grid.addWidget(self.rate_slider, 1, 0, 1, -1)
        self.setLayout(grid)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.execute)
        self.timer.start(ExecutionRateSlider.MAX_RATE // self.rate)

    @Slot()
    def execute(self) -> None:
        if self.run_state is RunState.PAUSED:
            pass
        elif self.run_state is RunState.RUNNING:
            self.step.emit()

    def set_state(self, state: RunState) -> None:
        self.run_state = state

    @Slot()
    def set_exec_rate(self, value: int) -> None:
        self.timer.setInterval(ExecutionRateSlider.MAX_RATE // value)

    @property
    def rate(self) -> int:
        return self.rate_slider.rate

    # @Slot(int)
    # def rate_changed(self, n):
    #     if n == self.MAX_RATE:


