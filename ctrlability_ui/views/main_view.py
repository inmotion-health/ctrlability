import logging

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget, QStackedWidget, QScrollArea, QPushButton

from ctrlability_ui.views.home_view import HomeView
from ctrlability_ui.views.head_face_view import HeadFaceView
from ctrlability_ui.views.hand_view import HandView
from ctrlability_ui.views.holistic_view import HolisticView
from ctrlability_ui.views.speech_view import SpeechView
from ctrlability_ui.views.log_view import LogViewer, QTextEditLogger

log = logging.getLogger(__name__)


class MainView(QWidget):

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.process = QPushButton("PROCESS", self)
        self.process.setCheckable(True)
        self.process.setChecked(True)
        self.layout.addWidget(self.process)

        # Create a QScrollArea
        self.scrollArea = QScrollArea(self)
        self.layout.addWidget(self.scrollArea)

        # Create a QStackedWidget that will contain the different views
        self.contentStack = QStackedWidget()
        self.scrollArea.setWidget(self.contentStack)
        self.scrollArea.setWidgetResizable(True)  # Allow the widget to be resized

        self.homeView = HomeView()
        self.headFaceView = HeadFaceView()
        self.handView = HandView()
        self.holisticView = HolisticView()
        self.speechView = SpeechView()
        self.log_viewer = LogViewer()
        self.setup_logging(self.log_viewer.log_view)

        # Create instances of the content views and add them to the stacked widget
        self.contentStack.addWidget(self.homeView)
        self.contentStack.addWidget(self.headFaceView)
        self.contentStack.addWidget(self.handView)
        self.contentStack.addWidget(self.holisticView)
        self.contentStack.addWidget(self.speechView)
        self.contentStack.addWidget(self.log_viewer)

        self.setMinimumSize(1000, 700)  # Set a minimum size for the main view

    def display_index(self, index):
        if 0 <= index < self.contentStack.count():
            self.contentStack.setCurrentIndex(index)
        else:
            self.contentStack.setCurrentWidget(QLabel("Select a page"))

    def setup_logging(self, log_widget):
        log_handler = QTextEditLogger(log_widget)
        logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
        logger = logging.getLogger()
        logger.addHandler(log_handler)
