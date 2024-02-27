import logging

# FIX_MK yaml should be imported from ctrlability.core.config_parser
# import yaml
from ruamel.yaml import YAML

from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QMenu,
    QWidget,
    QListWidget,
    QListWidgetItem,
)

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction

from ctrlability_ui.views.main_view import MainView

log = logging.getLogger(__name__)


# View
class CtrlAbilityView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CTRLABILITY")
        # self.setGeometry(100, 100, 200, 100)

        self.initMenu()
        self.initUI()

    def update(self, state):
        # if "selected_index" in state:
        #     self.comboBox.setCurrentIndex(state["selected_index"])
        print(f"-----------------------View updated with state: {state}")

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

        menu = ["HOME", "HEAD & FACE", "HAND", "SKELETON", "SPEECH", "LOG"]
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
