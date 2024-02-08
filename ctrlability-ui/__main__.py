import logging
import sys
import subprocess
import platform

# FIX_MK yaml should be imported from ctrlability.core.config_parser
import yaml

import pyautogui
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


log = logging.getLogger(__name__)


class WebcamRoiWidget(QLabel):
    roi_added = Signal(QRect)

    def __init__(self):
        super().__init__()
        self.rois = []  # List of QRect objects representing the ROIs
        self.current_pixmap = None
        self.current_roi = None
        self.is_drawing = False
        self.edit_state = False
        self.collided_roi_index = -1
        self.toggle_state_last = 0
        self.demo_mode = "TOGGLE_KEYS"

        self.msg = ""
        self.show_text = False

    def _add_roi(self, roi):
        self.rois.append(roi)
        self.roi_added.emit(roi)  # Emit the signal with the new ROI

    def set_image(self, pixmap):
        self.current_pixmap = pixmap
        self.update()  # Schedule a repaint

    def mousePressEvent(self, event):
        if self.edit_state:  # Check if the edit button is toggled
            self.is_drawing = True
            self.current_roi = QRect(event.position().toPoint(), QSize(0, 0))

    def mouseMoveEvent(self, event):
        if self.is_drawing:
            self.current_roi.setBottomRight(event.position().toPoint())
            self.update()

    def mouseReleaseEvent(self, event):
        if self.is_drawing:
            self._add_roi(self.current_roi)
            self.is_drawing = False
            self.update()

    def setEditState(self, state):
        self.edit_state = state

    def set_collision(self, index):
        self.collided_roi_index = index

    def set_msg(self, msg):
        self.msg = msg
        self.show_text = True
        QTimer.singleShot(5000, self._hideText)
        self.update()

    def _hideText(self):
        self.show_text = False
        self.update()  # This will trigger a repaint of the widget

    def _showText(self, painter, width, height, text):
        # Set the color for the text
        color = QColor(255, 0, 0)  # This is red. Adjust RGB values as needed.
        pen = QPen(color)
        painter.setPen(pen)

        font = painter.font()
        font.setPointSize(24)
        painter.setFont(font)

        # Calculate the position to draw the text
        text = self.msg
        font_metrics = QFontMetrics(font)
        text_width = font_metrics.boundingRect(text).width()
        text_height = font_metrics.height()

        x = (width - text_width) / 2
        y = (height + text_height) / 2  # + because the y-coordinate is the baseline of the text

        # Draw the text at the calculated position
        painter.drawText(x, y, text)

    def paintEvent(self, event):
        super().paintEvent(event)

        if self.current_pixmap:
            painter = QPainter(self)
            painter.drawPixmap(0, 0, self.current_pixmap)

            painter.setPen(QPen(Qt.black, 2))
            painter.setBrush(QBrush(QColor(0, 255, 0, 127)))  # Semi-transparent green

            for index, roi in enumerate(self.rois):
                if index == self.collided_roi_index:  # Check if the current ROI is the collided one
                    painter.setBrush(QBrush(QColor(255, 0, 0, 127)))  # red
                else:
                    painter.setBrush(QBrush(QColor(0, 255, 0, 127)))  # green
                painter.drawRect(roi)

            if self.demo_mode == "TOGGLE_KEYS":
                if self.collided_roi_index == -1:
                    self.toggle_state_last = 0
                elif self.collided_roi_index == 0 and self.toggle_state_last == 0:
                    pyautogui.keyDown("space")
                    # pyautogui.scroll(10)
                    print("space")
                    self.toggle_state_last = 1
                elif self.collided_roi_index == 1 and self.toggle_state_last == 0:
                    # pyautogui.press("w")
                    pyautogui.keyDown("w")
                    # pyautogui.scroll(-10)
                    self.toggle_state_last = 1

            if self.demo_mode == "SCROLL":
                if self.collided_roi_index == 0:
                    pyautogui.scroll(-1)
                elif self.collided_roi_index == 1:
                    pyautogui.scroll(1)

            if self.is_drawing and self.current_roi:
                painter.drawRect(self.current_roi)

            if self.show_text == True:
                self._showText(painter, self.current_pixmap.width(), self.current_pixmap.height(), self.msg)

            painter.end()
        else:
            painter = QPainter(self)
            width = 640
            height = 480
            painter.setPen(QPen(Qt.black, 2))
            painter.setBrush(QBrush(QColor(0, 0, 0, 0)))  # Semi-transparent green
            painter.drawRect(0, 0, width, height)
            if self.show_text == True:
                self._showText(painter, width, height, self.msg)

            painter.end()


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

        self.setMinimumSize(400, 300)  # Set a minimum size for the main view

    def display_index(self, index):
        if 0 <= index < self.contentStack.count():
            self.contentStack.setCurrentIndex(index)
        else:
            self.contentStack.setCurrentWidget(QLabel("Select a page"))


# Separate classes for each content type
class PreferencesView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        # Add checkboxes
        # for i in range(3):
        #     layout.addWidget(QCheckBox(f"Option {i+1}"))


class HeadFaceView(QWidget):

    # cam_changed = Signal(int)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        self.cam_combo_box = QComboBox(self)
        self.cam_combo_box.addItem("CAM1")
        self.cam_combo_box.addItem("CAM2")
        # self.cam_combo_box.currentIndexChanged.connect(self.on_select_cam)
        # self.cam_combo_box.setFixedWidth(250)
        layout.addWidget(self.cam_combo_box)

        # Add sliders
        for i in range(3):
            layout.addWidget(QSlider())

    # @Slot(int)
    # def on_select_cam(self, index):
    #     selected_text = self.cam_combo_box.currentText()
    #     log.debug(f"Selected cam: {selected_text}")
    #     self.cam_changed.emit(index)


class HandView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        # Add text fields
        # for i in range(10):
        #     layout.addWidget(QLineEdit(f"Text Field {i+1}"))


class HolisticView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        # Add a single slider
        layout.addWidget(QSlider())


# View
class CtrlAbilityView(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CTRLABILITY")
        # self.setGeometry(100, 100, 200, 100)

        self.initMenu()
        self.initUI()

    def update(self, state):
        if "selected_index" in state:
            self.comboBox.setCurrentIndex(state["selected_index"])
        print(f"View updated with state: {state}")

    def initMenu(self):
        # Create a menu bar
        menuBar = self.menuBar()

        # Create a About menu
        aboutMenu = menuBar.addMenu("&About")
        fileMenu = menuBar.addMenu("&File")

        # Create an action for the About dialog
        self.aboutAction = QAction("&About", self)
        self.aboutAction.setStatusTip("Show the About dialog")
        aboutMenu.addAction(self.aboutAction)

        self.loadAction = QAction("&Load", self)
        self.loadAction.setStatusTip("Load a file")
        fileMenu.addAction(self.loadAction)

        self.saveAction = QAction("&Save", self)
        self.saveAction.setStatusTip("Save the file")
        fileMenu.addAction(self.saveAction)

        # Create Help menu
        helpMenu = QMenu("&Help", self)
        menuBar.addMenu(helpMenu)

        # Create About action
        self.helpAction = QAction("&Help", self)
        self.helpAction.setStatusTip("Show the Help dialog")
        helpMenu.addAction(self.helpAction)
        # Set the appropriate role for macOS (optional, for better macOS integration)
        self.aboutAction.setMenuRole(QAction.MenuRole.AboutRole)

    def initUI(self):
        # Create the side menu (sidebar)
        self.sideMenu = QListWidget()
        self.sideMenu.setMinimumWidth(200)  # Set a minimum width for the sidebar

        menu = ["PREFERENCES", "HEAD & FACE", "HAND", "HOLISTIC"]
        for item in menu:

            listItem = QListWidgetItem(item)
            listItem.setFlags(listItem.flags() | Qt.ItemFlag.ItemIsUserCheckable)  # make the item checkable
            listItem.setCheckState(Qt.CheckState.Unchecked)  # initially unchecked
            self.sideMenu.addItem(listItem)

        # Create the main view
        self.mainView = MainView()

        # Create the main layout (horizontal) and add the side menu and the main view to it
        self.mainLayout = QHBoxLayout()
        self.mainLayout.addWidget(self.sideMenu, 1)  # Sidebar takes less space
        self.mainLayout.addWidget(self.mainView, 4)  # Main view takes more space

        # Create a central widget, set the main layout on it, and set it as the central widget
        self.centralWidget = QWidget()
        self.centralWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.centralWidget)


class ProcessThread(QThread):

    finished = Signal()

    def run(self):
        from ctrlability.core import bootstrapper

        stream_handlers = bootstrapper.boot()

        if log.isEnabledFor(logging.DEBUG):
            from ctrlability.util.tree_print import TreePrinter

            tree_printer = TreePrinter(stream_handlers, bootstrapper._mapping_engine)
            tree_printer.print_representation()
        while True:
            try:
                for stream in stream_handlers:
                    stream.process(None)
            except KeyboardInterrupt:
                log.info("KeyboardInterrupt: Exiting...")
                self.finished.emit()


# Model
class CtrlAbilityModel:
    def __init__(self):
        self.state = {}

    def load_state(self):
        try:
            with open("project_state.yaml", "r") as file:
                self.state = yaml.safe_load(file) or {}
        except FileNotFoundError:
            self.state = {}

    def save_state(self):
        with open("project_state.yaml", "w") as file:
            yaml.dump(self.state, file)

    def update_state(self, key, value):
        self.state[key] = value
        self.save_state()
        CtrlAbilityStateObserver.notify(self.state)


# Observer
class CtrlAbilityStateObserver:
    _observers = []

    @classmethod
    def register(cls, observer):
        cls._observers.append(observer)

    @classmethod
    def notify(cls, state):
        for observer in cls._observers:
            observer.update(state)


# Controller
class CtrlAbilityController(QObject):
    def __init__(self, model, view):
        super().__init__()
        self.model = model
        self.view = view
        CtrlAbilityStateObserver.register(self.view)
        self.view.sideMenu.itemClicked.connect(self.on_side_menu_item_clicked)

        ## Menu actions
        self.view.aboutAction.triggered.connect(self.show_about_dialog)
        self.view.loadAction.triggered.connect(self.load_file)
        self.view.saveAction.triggered.connect(self.save_file)
        self.view.helpAction.triggered.connect(self.show_help_dialog)

        ## HeadFaceView actions
        self.view.mainView.headFaceView.cam_combo_box.currentIndexChanged.connect(self.head_face_view_on_cam_changed)

        self.model.load_state()
        self.view.update(self.model.state)

        self.processThread = ProcessThread()
        self.processThread.finished.connect(self.on_process_thread_finished)

        # Use a QTimer to delay the centering by 500 milliseconds
        # QTimer.singleShot(500, self.center_on_screen)
        self.center_on_screen()

    # -----------------------------------
    # LOAD/SAVE YAML PROCESS CONFIG FILE
    # -----------------------------------

    def load_file(self):
        # FIX_MK start/stop Thread when new file is loaded
        self.stopProcessThread()
        from ctrlability.core.config_parser import ConfigParser

        fileName, _ = QFileDialog.getOpenFileName(self.view, "Open File", "", "CTRLABILITY CONFIG YAML (*.yaml)")
        if fileName:
            # Code to handle the file opening
            print(f"Loading {fileName}")
            ConfigParser.CONFIG_PATH = fileName
            self.startProcessThread()

    def save_file(self):
        fileName, _ = QFileDialog.getSaveFileName(self.view, "Save File", "", "All Files (*);;Text Files (*.txt)")
        if fileName:
            # Code to handle the file saving
            print(f"Saving to {fileName}")
            # self.stopProcess()

    # ----------------------------
    # UI Menu Actions
    # ----------------------------
    def on_side_menu_item_clicked(self, item):
        index = self.view.sideMenu.row(item)
        # Uncheck all other items
        for i in range(self.view.sideMenu.count()):
            if i != index:
                self.view.sideMenu.item(i).setCheckState(Qt.CheckState.Unchecked)
        self.view.mainView.display_index(index)
        self.model.update_state("side_menu_selected_index", index)

    def show_about_dialog(self):
        QMessageBox.about(self.view, "About", "This is the About dialog.\nAdd information about your application here.")

    def show_help_dialog(self):
        QMessageBox.about(self.view, "Help", "This is the HELP dialog.\nAdd information about your application here.")

    def center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()  # Get screen geometry
        window = self.view.geometry()  # Get window geometry
        self.view.move(
            (screen.width() - window.width()) / 2,
            (screen.height() - window.height()) / 2,
        )

    # ----------------------------
    # UI HeadFaceView Actions
    # ----------------------------
    def head_face_view_on_cam_changed(self, index):
        self.model.update_state("cam_selected_index", index)

    # ----------------------------
    # Thread Actions
    # ----------------------------
    def startProcessThread(self):
        print("Starting process")
        if not self.processThread.isRunning():
            self.processThread.start()

    def stopProcessThread(self):
        print("Stopping process")
        if self.processThread.isRunning():
            self.processThread.terminate()  # or implement a more graceful stop if possible
            self.processThread.wait()

    def on_process_thread_finished(self):
        print("Process finished.")


def show_version():
    from ctrlability import __version__

    printing.print_line()
    print("CTRLABILITY - Controller for people with motor disabilities")
    print(f"Version: {__version__}")
    exit(0)


def check_appearance():
    """Checks DARK/LIGHT mode of macos."""
    cmd = "defaults read -g AppleInterfaceStyle"
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    return bool(p.communicate()[0])


def runAPP():
    # initialize gui
    # ToDo: fix in deployment: currently development hack to show application name in menu bar
    if sys.platform == "darwin":
        from Foundation import NSBundle

        app_info = NSBundle.mainBundle().infoDictionary()
        app_info["CFBundleName"] = "CTRLABILITY"

    app = QApplication(sys.argv)
    app.setApplicationName("CTRLABILITY")  # Set the application name
    # app.setQuitOnLastWindowClosed(False)  # Keep the app running even if all windows are closed

    theme = "light_blue.xml"
    if platform.system() == "Darwin":
        if check_appearance():
            theme = "dark_blue.xml"
    apply_stylesheet(app, theme=theme)

    model = CtrlAbilityModel()
    view = CtrlAbilityView()
    controller = CtrlAbilityController(model, view)
    view.show()

    sys.exit(app.exec())


def setupParser():
    # set the config file path from the arguments
    from ctrlability.core.config_parser import ConfigParser

    ConfigParser.CONFIG_PATH = args.config_file


if __name__ == "__main__":
    args = parse_arguments()

    if args.show_version:
        show_version()

    setupParser()
    runAPP()
