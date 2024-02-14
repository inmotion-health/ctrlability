import logging

from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QWidget,
    QStackedWidget,
    QScrollArea,
)

from ctrlability_ui.views.preferences_view import PreferencesView
from ctrlability_ui.views.head_face_view import HeadFaceView
from ctrlability_ui.views.hand_view import HandView
from ctrlability_ui.views.holistic_view import HolisticView

log = logging.getLogger(__name__)


class MainView(QWidget):

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        # Create a QScrollArea
        self.scrollArea = QScrollArea(self)
        self.layout.addWidget(self.scrollArea)

        # Create a QStackedWidget that will contain the different views
        self.contentStack = QStackedWidget()
        self.scrollArea.setWidget(self.contentStack)
        self.scrollArea.setWidgetResizable(True)  # Allow the widget to be resized

        self.preferenceView = PreferencesView()
        self.headFaceView = HeadFaceView()
        self.handView = HandView()
        self.holisticView = HolisticView()

        # Create instances of the content views and add them to the stacked widget
        self.contentStack.addWidget(self.preferenceView)
        self.contentStack.addWidget(self.headFaceView)
        self.contentStack.addWidget(self.handView)
        self.contentStack.addWidget(self.holisticView)

        self.setMinimumSize(1000, 700)  # Set a minimum size for the main view

    def display_index(self, index):
        if 0 <= index < self.contentStack.count():
            self.contentStack.setCurrentIndex(index)
        else:
            self.contentStack.setCurrentWidget(QLabel("Select a page"))
