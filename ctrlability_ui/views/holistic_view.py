import logging
import sys
import subprocess
import platform

# FIX_MK yaml should be imported from ctrlability.core.config_parser
# import yaml
from ruamel.yaml import YAML
import pyautogui

# from vidcontrol import VideoManager


from PySide6.QtCore import QObject, QRect, QSize, Qt, QThread, QTimer, Signal, Slot
from PySide6.QtGui import (
    QAction,
    QBrush,
    QColor,
    QFont,
    QFontMetrics,
    QKeySequence,
    QPainter,
    QPen,
    QPixmap,
    QShortcut,
    QIcon,
    QImage,
)
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QPushButton,
    QSystemTrayIcon,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QStackedWidget,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QFileDialog,
    QScrollArea,
    QSlider,
    QLineEdit,
    QCheckBox,
)
from qt_material import apply_stylesheet, list_themes

import ctrlability.util.printing as printing
from ctrlability.util.argparser import parse_arguments

from PySide6.QtWidgets import QWidget, QVBoxLayout, QSlider

log = logging.getLogger(__name__)


class HolisticView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        # Add a single slider
        layout.addWidget(QSlider())
