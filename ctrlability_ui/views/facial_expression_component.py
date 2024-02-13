import sys
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QFormLayout,
    QComboBox,
    QLabel,
    QProgressBar,
    QSlider,
    QLineEdit,
    QVBoxLayout,
    QFrame,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPixmap, QPainter


class LEDIndicator(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_indicator(False)

    def set_indicator(self, on):
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setBrush(QColor("green") if on else QColor("red"))
        painter.drawEllipse(0, 0, 15, 15)
        painter.end()
        self.setPixmap(pixmap)


class FacialExpressionComponent(QWidget):
    def __init__(self):
        super().__init__()
        self.blendshapes = [
            "_neutral",
            "browDownLeft",
            "browDownRight",
            "browInnerUp",
            "browOuterUpLeft",
            "browOuterUpRight",
            "cheekPuff",
            "cheekSquintLeft",
            "cheekSquintRight",
            "eyeBlinkLeft",
            "eyeBlinkRight",
            "eyeLookDownLeft",
            "eyeLookDownRight",
            "eyeLookInLeft",
            "eyeLookInRight",
            "eyeLookOutLeft",
            "eyeLookOutRight",
            "eyeLookUpLeft",
            "eyeLookUpRight",
            "eyeSquintLeft",
            "eyeSquintRight",
            "eyeWideLeft",
            "eyeWideRight",
            "jawForward",
            "jawLeft",
            "jawOpen",
            "jawRight",
            "mouthClose",
            "mouthDimpleLeft",
            "mouthDimpleRight",
            "mouthFrownLeft",
            "mouthFrownRight",
            "mouthFunnel",
            "mouthLeft",
            "mouthLowerDownLeft",
            "mouthLowerDownRight",
            "mouthPressLeft",
            "mouthPressRight",
            "mouthPucker",
            "mouthRight",
            "mouthRollLower",
            "mouthRollUpper",
            "mouthShrugLower",
            "mouthShrugUpper",
            "mouthSmileLeft",
            "mouthSmileRight",
            "mouthStretchLeft",
            "mouthStretchRight",
            "mouthUpperUpLeft",
            "mouthUpperUpRight",
            "noseSneerLeft",
            "noseSneerRight",
        ]
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        form_container = QFrame()
        form_container.setFrameShape(QFrame.StyledPanel)
        form_layout = QFormLayout()

        self.expression_dropdown = QComboBox()
        for expression in self.blendshapes:
            self.expression_dropdown.addItem(expression)
        self.expression_dropdown.setFixedWidth(200)
        form_layout.addRow(QLabel("Expression:"), self.expression_dropdown)

        confidence_layout = QHBoxLayout()
        self.confidence_progress_bar = QProgressBar()
        self.confidence_progress_bar.setFixedWidth(200)
        confidence_layout.addWidget(self.confidence_progress_bar)
        form_layout.addRow(QLabel("Confidence:"), confidence_layout)

        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setMinimum(0)
        self.threshold_slider.setMaximum(100)
        self.threshold_slider.setValue(50)  # Default threshold
        self.threshold_slider.setFixedWidth(200)
        self.threshold_slider.valueChanged.connect(self.check_trigger_condition)
        form_layout.addRow(QLabel("Threshold:"), self.threshold_slider)

        action_layout = QHBoxLayout()
        self.led_indicator = LEDIndicator()
        self.action_text_field = QLineEdit()
        self.action_text_field.setFixedWidth(170)
        action_layout.addWidget(self.action_text_field)
        action_layout.addWidget(self.led_indicator)
        form_layout.addRow(QLabel("Action:"), action_layout)

        form_container.setLayout(form_layout)
        main_layout.addWidget(form_container)

    def simulate_confidence_change(self, confidence):
        self.confidence_progress_bar.setValue(confidence)
        self.check_trigger_condition()

    def check_trigger_condition(self):
        confidence = self.confidence_progress_bar.value()
        threshold = self.threshold_slider.value()
        self.led_indicator.set_indicator(confidence > threshold)
