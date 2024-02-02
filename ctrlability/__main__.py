import logging
import sys
import subprocess
import platform

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
)
from qt_material import apply_stylesheet, list_themes

import ctrlability.util.printing as printing
from ctrlability.util.argparser import parse_arguments


log = logging.getLogger(__name__)


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


class MainView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        # Create a QScrollArea
        self.scrollArea = QScrollArea(self)
        self.layout.addWidget(self.scrollArea)

        # Create a widget that will contain the content
        self.contentWidget = QWidget()
        self.scrollArea.setWidget(self.contentWidget)
        self.scrollArea.setWidgetResizable(True)  # Allow the widget to be resized

        # Set the layout for the content widget
        self.contentLayout = QVBoxLayout(self.contentWidget)

        # Add a label as placeholder content (you can add more widgets here)
        self.label = QLabel("Welcome @ CTRLABILITY ", self.contentWidget)
        self.contentLayout.addWidget(self.label)

        self.setMinimumSize(400, 300)  # Set a minimum size for the main view

    def display_index(self, index):
        # self.label.setText(f"Current Page: {index + 1}")  # Update the label to display the index
        if index == 0:
            self.showPreferences()
        elif index == 1:
            self.showHeadFace()
        elif index == 2:
            self.showHand()
        elif index == 3:
            self.showHolistic()
        else:
            self.label.setText("Select a page")

    def showPreferences(self):
        self.label.setText("Preferences")

    def showHeadFace(self):
        self.label.setText("head & face")

    def showHand(self):
        self.label.setText("hand")

    def showHolistic(self):
        self.label.setText("holistic")


class CtrlAbilityApp(QMainWindow):
    def __init__(self, app):
        super().__init__()

        self.app = app
        self.setWindowTitle("CTRLABILITY")
        # self.setGeometry(100, 100, 800, 600)
        # self.setWindowIcon(QIcon("ctrlability/assets/icons/ctrlability_icon.png"))

        self.processThread = ProcessThread()
        self.processThread.finished.connect(self.onProcessFinished)

        self.initMenu()
        self.initUI()

    def load_file(self):
        # self.stopProcess()
        from ctrlability.core.config_parser import ConfigParser

        fileName, _ = QFileDialog.getOpenFileName(self, "Open File", "", "CTRLABILITY CONFIG YAML (*.yaml)")
        if fileName:
            # Code to handle the file opening
            print(f"Loading {fileName}")
            ConfigParser.CONFIG_PATH = fileName
            self.startProcess()

    def save_file(self):
        fileName, _ = QFileDialog.getSaveFileName(self, "Save File", "", "All Files (*);;Text Files (*.txt)")
        if fileName:
            # Code to handle the file saving
            print(f"Saving to {fileName}")
            self.stopProcess()

    def startProcess(self):
        print("Starting process")
        if not self.processThread.isRunning():
            self.processThread.start()

    def stopProcess(self):
        print("Stopping process")
        if self.processThread.isRunning():
            self.processThread.terminate()  # or implement a more graceful stop if possible
            self.processThread.wait()

    def onProcessFinished(self):
        print("Process finished or stopped.")

    def show_about_dialog(self):
        QMessageBox.about(self, "About", "This is the About dialog.\nAdd information about your application here.")

    def show_help_dialog(self):
        QMessageBox.about(self, "Help", "This is the HELP dialog.\nAdd information about your application here.")

    def initMenu(self):
        # Create a menu bar
        menuBar = self.menuBar()

        # Create a About menu
        aboutMenu = menuBar.addMenu("&About")
        fileMenu = menuBar.addMenu("&File")

        # Create an action for the About dialog
        aboutAction = QAction("&About", self)
        aboutAction.setStatusTip("Show the About dialog")
        aboutAction.triggered.connect(self.show_about_dialog)
        aboutMenu.addAction(aboutAction)

        loadAction = QAction("&Load", self)
        loadAction.setStatusTip("Load a file")
        loadAction.triggered.connect(self.load_file)
        fileMenu.addAction(loadAction)

        saveAction = QAction("&Save", self)
        saveAction.setStatusTip("Save the file")
        saveAction.triggered.connect(self.save_file)
        fileMenu.addAction(saveAction)

        # Create Help menu
        helpMenu = QMenu("&Help", self)
        menuBar.addMenu(helpMenu)

        # Create About action
        helpAction = QAction("&Help", self)
        helpAction.setStatusTip("Show the Help dialog")
        helpAction.triggered.connect(self.show_help_dialog)
        helpMenu.addAction(helpAction)
        # Set the appropriate role for macOS (optional, for better macOS integration)
        aboutAction.setMenuRole(QAction.MenuRole.AboutRole)

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

        self.sideMenu.itemClicked.connect(self.menu_item_clicked)  # connect the click event

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

    def menu_item_clicked(self, item):
        # Get the index of the clicked item
        index = self.sideMenu.row(item)
        # Uncheck all other items
        for i in range(self.sideMenu.count()):
            if i != index:
                self.sideMenu.item(i).setCheckState(Qt.CheckState.Unchecked)
        # Display the index in the main view
        self.mainView.display_index(index)

    def start_button_clicked(self):
        print("Start button clicked")
        # self.hide()
        # subprocess.Popen(["python3", "ctrlability/__main__.py"])

    def quit_button_clicked(self):
        self.app.quit()


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

    mainWin = CtrlAbilityApp(app)
    mainWin.show()
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
