import sys

from PySide6.QtGui import (
    QImage,
    QPixmap,
    QKeySequence,
    QIcon,
    QShortcut,
    QAction,
)
from PySide6.QtCore import QTimer, Qt, Slot, QThread, Signal, QObject
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QCheckBox,
    QSlider,
    QWidget,
    QMenuBar,
    QMenu,
    QSystemTrayIcon,
    QComboBox,
    QTabWidget,
)
from qt_material import apply_stylesheet, list_themes
import logging as log

import Video.SourceProvider
import MouseController
from MediaPipeThread import MediaPipeThread
from Util.ArgumentParser import parse_arguments


class SystemTrayApp(QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        super(SystemTrayApp, self).__init__(icon, parent)
        self.setToolTip("Virtual Keyboard Access")

        # Create the menu
        self.menu = QMenu(parent)

        # Create an action for opening the virtual keyboard
        self.open_keyboard_action = QAction("Open Virtual Keyboard", self)
        self.open_keyboard_action.triggered.connect(self.open_virtual_keyboard)

        # Add the action to the menu
        self.menu.addAction(self.open_keyboard_action)

        # Add a quit action to the menu
        self.quit_action = QAction("Quit", self)
        self.quit_action.triggered.connect(app.quit)
        self.menu.addAction(self.quit_action)

        # Set the context menu for the system tray
        self.setContextMenu(self.menu)

    def open_virtual_keyboard(self):
        # Code to open the virtual keyboard
        log.info("Virtual Keyboard opened!")


class WebCamTabView(QObject):
    cam_index_changed = Signal(int)

    def __init__(self, main):
        super().__init__()
        self._cam_index = 0
        self.webCamWidget = QWidget()

        self.webCamLayoutView = QHBoxLayout()

        # Webcam display area (equivalent to BorderLayout::Center)
        self.label = QLabel(main)
        self.webCamLayoutView.addWidget(self.label)

        # Settings area (equivalent to BorderLayout::East)
        settings_layout = QVBoxLayout()

        # Create a QVBoxLayout for the buttons, labels, and sliders
        grouped_layout = QVBoxLayout()

        # Create a QComboBox to liste the connected webcames
        self.webcam_combo_box = QComboBox(main)
        webcam_dict = Video.SourceProvider.get_available_vidsources()
        for key, value in webcam_dict.items():
            self.webcam_combo_box.addItem(value)
        self.webcam_combo_box.setFixedWidth(250)
        grouped_layout.addWidget(self.webcam_combo_box)

        # Connect the activated signal to our custom slot
        self.webcam_combo_box.currentIndexChanged.connect(self.on_select_camsource)

        # Create the checkbox
        self.tracking_checkbox = QCheckBox("Tracking", main)
        # Connect the checkbox's state change signal to the callback
        self.tracking_checkbox.stateChanged.connect(self.tracking_callback)
        grouped_layout.addWidget(self.tracking_checkbox)

        # Adding buttons to the grouped layout
        self.buttons = []
        for i in range(4):
            btn = QPushButton(f"Button {i+1}", main)
            self.buttons.append(btn)
            grouped_layout.addWidget(btn)

        # Adding labels and sliders just below the buttons
        self.sliders = []
        for i in range(4):
            lbl = QLabel(f"Slider {i+1}", main)
            slider = QSlider(Qt.Horizontal, main)
            slider.valueChanged.connect(self.slider_callback)  # Connect the callback to valueChanged signal
            self.sliders.append(slider)
            grouped_layout.addWidget(lbl)
            grouped_layout.addWidget(slider)

        # Add the grouped layout to settings layout
        settings_layout.addLayout(grouped_layout)

        # Push the remaining space to the bottom
        settings_layout.addStretch()

        self.webCamLayoutView.addLayout(settings_layout)
        self.webCamWidget.setLayout(self.webCamLayoutView)

    def updateWebcamFrame(self, pixmap):
        self.label.setPixmap(pixmap)

    @Slot(int)
    def on_select_camsource(self, index):
        self._cam_index = index
        self.cam_index_changed.emit(self._cam_index)

    def tracking_callback(self, state):
        if state == 0:
            MouseController.set_tracking_mode(False)

        elif state == 2:
            MouseController.set_tracking_mode(True)
            MouseController.set_cursor_center()

    def toggle_tracking(self):
        current_state = self.tracking_checkbox.isChecked()
        self.tracking_checkbox.setChecked(not current_state)

    def slider_callback(self, value):
        sender = self.sender()  # Find out which slider sent the signal
        index = self.sliders.index(sender) + 1  # Get the slider number (1-based)
        log.debug(f"Slider {index} value changed to: {value}")


class MediaPipeApp(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app  # Store the QApplication reference here

        self.setWindowTitle("CTRLABILITY")
        self.setupMenuBar()

        # Create the QTabWidget
        self.tab_widget = QTabWidget()

        # First tab for Video Processing
        tab1 = QWidget()
        tab1_layout = QVBoxLayout(tab1)
        self.webcam_tab_view1 = WebCamTabView(self)
        tab1_layout.addWidget(self.webcam_tab_view1.webCamWidget)
        self.tab_widget.addTab(tab1, "Video Processing 1")

        # Second tab for Video Processing
        tab2 = QWidget()
        tab2_layout = QVBoxLayout(tab2)
        self.webcam_tab_view2 = WebCamTabView(self)
        tab2_layout.addWidget(self.webcam_tab_view2.webCamWidget)
        self.tab_widget.addTab(tab2, "Video Processing 2")

        self.setCentralWidget(self.tab_widget)

        # Create a shortcut for the 'T' key
        self.shortcut = QShortcut(QKeySequence(Qt.Key_T), self)
        self.shortcut.activated.connect(self.toggle_tracking_by_shortcut)

        # Use a QTimer to delay the centering by 2000 milliseconds
        QTimer.singleShot(4000, self.center_on_screen)

        # Setup Threads for First Video Processing
        self.thread1 = QThread()
        self.worker1 = MediaPipeThread(0)
        self.worker1.moveToThread(self.thread1)
        self.setup_connections(self.thread1, self.worker1)

        self.thread2 = QThread()
        self.worker2 = MediaPipeThread(0)
        self.worker2.moveToThread(self.thread2)
        self.setup_connections(self.thread2, self.worker2)

        self.thread1.start()
        self.thread2.start()

        # call cam1_changed when cam_index_changed signal is emitted
        self.webcam_tab_view1.cam_index_changed.connect(self.cam1_changed)
        # call cam2_changed when cam_index_changed signal is emitted
        self.webcam_tab_view2.cam_index_changed.connect(self.cam2_changed)

    @Slot(int)
    def cam1_changed(self, index):
        self.worker1.handle_cam_index_change(index)

    @Slot(int)
    def cam2_changed(self, index):
        self.worker2.handle_cam_index_change(index)

    # setup video processing threads
    def setup_connections(self, thread, worker):
        worker.finished.connect(self.on_finished)
        worker.signalFrame.connect(self.on_progress)
        thread.started.connect(worker.process)

    # cleanup video processing threads
    def on_finished(self):
        if not self.thread1.isRunning() and not self.thread2.isRunning():
            self.thread1.quit()
            self.thread2.quit()
            self.thread1.wait()
            self.thread2.wait()

    # when a frame is processed, update the webcam frame
    def on_progress(self, qImg):
        sender = self.sender()

        if sender == self.worker1:
            pixmap = QPixmap.fromImage(qImg)
            self.webcam_tab_view1.updateWebcamFrame(pixmap)
        elif sender == self.worker2:
            pixmap = QPixmap.fromImage(qImg)
            self.webcam_tab_view2.updateWebcamFrame(pixmap)

    def toggle_tracking_by_shortcut(self):
        if self.tab_widget.currentIndex() == 0:
            self.webcam_tab_view1.toggle_tracking()
        elif self.tab_widget.currentIndex() == 1:
            self.webcam_tab_view2.toggle_tracking()

    def setupMenuBar(self):
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)

        themeMenu = QMenu("Themes", self)
        menubar.addMenu(themeMenu)

        for theme in list_themes():
            themeMenu.addAction(theme, lambda theme_name=theme: self.applyTheme(theme_name))

    def applyTheme(self, theme_name):
        apply_stylesheet(self.app, theme=theme_name)  # apply the chosen theme

    def center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()  # Get screen geometry
        window = self.geometry()  # Get window geometry
        self.move(
            (screen.width() - window.width()) / 2,
            (screen.height() - window.height()) / 2,
        )

    def closeEvent(self, event):
        self.thread1.terminate()
        self.thread2.terminate()
        event.accept()
        self.app.quit()


if __name__ == "__main__":
    # ToDo: fix in deployment: currently development hack to show application name in menu bar
    if sys.platform == "darwin":
        from Foundation import NSBundle

        app_info = NSBundle.mainBundle().infoDictionary()
        app_info["CFBundleName"] = "CTRLABILITY"

    parse_arguments()

    app = QApplication(sys.argv)
    app.setApplicationName("CTRLABILITY")  # Set the application name
    # setup stylesheet
    apply_stylesheet(app, theme="light_blue.xml")

    # Ensure the app doesn't exit when the window is closed
    app.setQuitOnLastWindowClosed(False)

    # Setup the system tray icon
    # icon = QIcon("./assets/minimize.png")  # Replace with the path to your icon
    # tray = SystemTrayApp(icon)
    # tray.show()

    mainWin = MediaPipeApp(app)
    mainWin.show()
    sys.exit(app.exec())
