import logging
from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QSpacerItem,
    QSizePolicy,
)

from ctrlability_ui.views.mouse_settings_component import MouseSettingsComponent

log = logging.getLogger(__name__)


# Separate classes for each content type
class PreferencesView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.mouse_settings = MouseSettingsComponent()
        layout.addWidget(self.mouse_settings)

        # Add a spacer item at the bottom to push everything up
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)

        # Add checkboxes
        # for i in range(3):
        #     layout.addWidget(QCheckBox(f"Option {i+1}"))
