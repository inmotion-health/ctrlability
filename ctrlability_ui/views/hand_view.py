import logging
from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget,
)

log = logging.getLogger(__name__)


class HandView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        # Add text fields
        # for i in range(10):
        #     layout.addWidget(QLineEdit(f"Text Field {i+1}"))
