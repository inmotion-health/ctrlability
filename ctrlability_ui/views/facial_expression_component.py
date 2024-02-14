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
    QPushButton,
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
        self.expression_dropdown.setFixedWidth(300)
        form_layout.addRow(QLabel("Expression:"), self.expression_dropdown)

        confidence_layout = QHBoxLayout()
        self.confidence_progress_bar = QProgressBar()
        self.confidence_progress_bar.setFixedWidth(300)
        confidence_layout.addWidget(self.confidence_progress_bar)
        form_layout.addRow(QLabel("Confidence:"), confidence_layout)

        self.threshold = QSlider(Qt.Horizontal)
        self.threshold.setMinimum(0)
        self.threshold.setMaximum(100)
        self.threshold.setValue(50)  # Default threshold
        self.threshold.setFixedWidth(300)
        self.threshold.valueChanged.connect(self.check_trigger_condition)
        form_layout.addRow(QLabel("Threshold:"), self.threshold)

        action_layout = QHBoxLayout()
        self.led_indicator = LEDIndicator()
        self.action_type = QComboBox()
        self.action_type.addItems(["key", "mouse"])
        self.action_type.setFixedWidth(100)

        self.action_text_field = QLineEdit()
        self.action_text_field.setFixedWidth(170)
        action_layout.addWidget(self.action_type)
        action_layout.addWidget(self.action_text_field)
        action_layout.addWidget(self.led_indicator)
        form_layout.addRow(QLabel("Action:"), action_layout)

        self.action_type_changed()  # Set default placeholder text
        self.action_type.currentIndexChanged.connect(self.action_type_changed)

        # Add Save Button
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.on_save_clicked)
        form_layout.addRow(self.save_button)

        form_container.setLayout(form_layout)
        main_layout.addWidget(form_container)

    def simulate_confidence_change(self, confidence):
        self.confidence_progress_bar.setValue(confidence)
        self.check_trigger_condition()

    def check_trigger_condition(self):
        confidence = self.confidence_progress_bar.value()
        threshold = self.threshold.value()
        self.led_indicator.set_indicator(confidence > threshold)

    def on_save_clicked(self):
        print("Save button clicked")
        print(f"Expression: {self.expression_dropdown.currentText()}")
        print(f"Threshold: {self.threshold.value()}")
        print(f"Action: {self.action_text_field.text()}")

    def action_type_changed(self):
        print(f"Action Type changed to: {self.action_type.currentText()}")
        if self.action_type.currentText() == "key":
            self.action_text_field.setPlaceholderText("e.g. cmd,space or a")
            self.action_text_field.setToolTip("Enter a key or a combination of keys separated by comma")
        else:
            self.action_text_field.setPlaceholderText("e.g. left_down or right")
            self.action_text_field.setToolTip("Possibilites: 'left', 'right', 'double', 'left_down', and 'left_up'")
