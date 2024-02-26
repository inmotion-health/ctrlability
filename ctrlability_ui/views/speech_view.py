import logging
from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QWidget,
)
from qt_material import apply_stylesheet, list_themes

import ctrlability.util.printing as printing
from ctrlability.util.argparser import parse_arguments

from PySide6.QtWidgets import QWidget, QVBoxLayout, QSlider

log = logging.getLogger(__name__)


class SpeechView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        note = QLabel("TEMPLATE FOR SPEECH TO KEY/MOUSE CONTROL")
        note.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(note)
