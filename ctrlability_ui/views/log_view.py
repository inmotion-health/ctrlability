import logging

from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QPlainTextEdit,
)

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Slot


class QTextEditLogger(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.widget.setReadOnly(True)

    @Slot(str)
    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)


class LogViewer(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        self.log_view = QPlainTextEdit()
        layout.addWidget(self.log_view)
