import logging
from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget,
)

log = logging.getLogger(__name__)


# Separate classes for each content type
class PreferencesView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        # Add checkboxes
        # for i in range(3):
        #     layout.addWidget(QCheckBox(f"Option {i+1}"))
