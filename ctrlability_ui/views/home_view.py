import logging
from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QLabel,
)

log = logging.getLogger(__name__)


# Separate classes for each content type
class HomeView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        note = QLabel("WELCOME TO CTRLABILITY")
        note.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(note)
