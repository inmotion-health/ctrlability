import sys
from PySide6.QtWidgets import (
    QWidget,
    QFormLayout,
    QComboBox,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QFrame,
    QPushButton,
)


class MouseSettingsComponent(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        form_container = QFrame()
        form_container.setFrameShape(QFrame.StyledPanel)
        form_container.setFixedSize(400, 300)
        form_layout = QFormLayout()

        headline = QLabel("Mouse Settings")
        headline.setStyleSheet("font-size: 20px; font-weight: bold;")
        form_layout.addRow(headline)

        self.mode = QComboBox()
        self.mode.addItems(["relative", "absolute"])
        self.mode.setFixedWidth(200)
        form_layout.addRow(QLabel("Mode:"), self.mode)

        self.x_threshold = QLineEdit()
        self.x_threshold.setFixedWidth(200)
        self.x_threshold.setPlaceholderText("Default = 0.02")
        form_layout.addRow(QLabel("Threshold X:"), self.x_threshold)

        self.y_threshold = QLineEdit()
        self.y_threshold.setFixedWidth(200)
        self.y_threshold.setPlaceholderText("Default = 0.02")
        form_layout.addRow(QLabel("Threshold Y:"), self.y_threshold)

        self.x_velocity = QLineEdit()
        self.x_velocity.setFixedWidth(200)
        self.x_velocity.setPlaceholderText("Default = 0.05")
        form_layout.addRow(QLabel("Velocity X:"), self.x_velocity)

        self.y_velocity = QLineEdit()
        self.y_velocity.setFixedWidth(200)
        self.y_velocity.setPlaceholderText("Default = 0.5")
        form_layout.addRow(QLabel("Velocity Y:"), self.y_velocity)

        # Add Save Button
        self.save_button = QPushButton("Save")
        self.save_button.setFixedWidth(280)
        self.save_button.clicked.connect(self.on_save_clicked)
        form_layout.addRow(self.save_button)

        form_container.setLayout(form_layout)
        main_layout.addWidget(form_container)

    def on_save_clicked(self):
        print("Save button clicked")
        print(f"Mode: {self.mode.currentText()}")
        print(f"ThresholdX: {self.x_threshold.text()}")
        print(f"ThresholdY: {self.y_threshold.text()}")
        print(f"VelocityX: {self.x_velocity.text()}")
        print(f"VelocityY: {self.y_velocity.text()}")
