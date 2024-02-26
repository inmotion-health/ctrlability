import logging
from PySide6.QtWidgets import QVBoxLayout, QWidget, QLabel

log = logging.getLogger(__name__)


class HandView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        note = QLabel("TEMPLATE FOR HAND TRACKING")
        note.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(note)
