import logging as log
import sys

from PySide6.QtCore import QTimer, Qt, Slot, QThread, Signal, QObject, QRect, QSize
from PySide6.QtGui import QPixmap, QKeySequence, QShortcut, QAction, QPainter, QColor, QBrush, QPen, QFont, QFontMetrics
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QWidget,
    QMenuBar,
    QMenu,
    QSystemTrayIcon,
    QComboBox,
    QTabWidget,
)
from qt_material import apply_stylesheet, list_themes

from ctrlability.mp_thread import MediaPipeThread
import pyautogui
from ctrlability.util.argparser import parse_arguments
from vidcontrol import VideoManager


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


class WebCamTabView(QObject):
    cam_index_changed = Signal(int)
    tracking_state_changed = Signal(bool)
    process_state_changed = Signal(bool)
    mouse_ctrl_mode_changed = Signal(int)
    mp_model_changed = Signal(int)
    roi_changed = Signal(QRect)

    def __init__(self, main, video_manager: VideoManager):
        super().__init__()
        self._cam_index = 0
        self.video_manager = video_manager
        self.webCamWidget = QWidget()

        self.webCamLayoutView = QHBoxLayout()

        # Webcam display area (equivalent to BorderLayout::Center)
        self.label = QLabel(main)
        self.webCamLayoutView.addWidget(self.label)

        self.webcam_roi_region = WebcamRoiWidget()
        self.webcam_roi_region.roi_added.connect(self.on_new_roi_added)
        self.webcam_roi_region.setFixedSize(640, 480)
        self.webCamLayoutView.addWidget(self.webcam_roi_region)

        # Settings area (equivalent to BorderLayout::East)
        settings_layout = QVBoxLayout()

        # Create a QVBoxLayout for the buttons, labels, and sliders
        grouped_layout = QVBoxLayout()

        # Create the checkbox
        self.process_button = QPushButton("PROCESS", main)
        self.process_button.setCheckable(True)
        # Connect the checkbox's state change signal to the callback
        self.process_button.clicked.connect(self.process_callback)
        grouped_layout.addWidget(self.process_button)

        # Create a QComboBox to liste the available detection algorithms
        self.mp_model_combo_box = QComboBox(main)
        mp_models = ["Face", "Hands"]
        for value in mp_models:
            self.mp_model_combo_box.addItem(value)
        self.mp_model_combo_box.setFixedWidth(250)
        grouped_layout.addWidget(self.mp_model_combo_box)
        # Connect the activated signal to our custom slot
        self.mp_model_combo_box.currentIndexChanged.connect(self.on_select_mp_model)

        # Create a QComboBox to liste the connected webcames
        self.webcam_combo_box = QComboBox(main)
        webcam_dict = self.video_manager.list_available_cameras()
        for key, value in webcam_dict.items():
            self.webcam_combo_box.addItem(value)
        self.webcam_combo_box.setFixedWidth(250)
        # Initialize the last_selected_index with the current index
        self.cam_index_last_selected = self.webcam_combo_box.currentIndex()

        grouped_layout.addWidget(self.webcam_combo_box)
        # Connect the activated signal to our custom slot
        self.webcam_combo_box.currentIndexChanged.connect(self.on_select_camsource)

        # Create the checkbox
        self.tracking_button = QPushButton("TRACKING", main)
        self.tracking_button.setCheckable(True)
        # Connect the checkbox's state change signal to the callback
        self.tracking_button.clicked.connect(self.tracking_callback)
        grouped_layout.addWidget(self.tracking_button)

        # self.mouse_ctrl_mode_label = QLabel("Mouse Mode:", main)
        # grouped_layout.addWidget(self.mouse_ctrl_mode_label)
        # Create a QComboBox to list the available modes for mouse control
        self.mouse_ctrl_mode_ui = QComboBox(main)
        self.mouse_ctrl_mode_ui.addItem("relative")
        self.mouse_ctrl_mode_ui.addItem("absolute")
        # self.mouse_ctrl_mode_ui.setFixedWidth(250)
        grouped_layout.addWidget(self.mouse_ctrl_mode_ui)
        self.mouse_ctrl_mode_ui.currentIndexChanged.connect(self.on_select_mouse_ctrl_mode)

        self.edit_button = QPushButton("ADD ROI", main)
        self.edit_button.setCheckable(True)
        self.edit_button.clicked.connect(self.edit_button_callback)
        grouped_layout.addWidget(self.edit_button)

        # # Adding buttons to the grouped layout
        # self.buttons = []
        # for i in range(2):
        #     btn = QPushButton(f"Dummy Button {i+1}", main)
        #     self.buttons.append(btn)
        #     grouped_layout.addWidget(btn)

        # # Adding labels and sliders just below the buttons
        # self.sliders = []
        # for i in range(2):
        #     lbl = QLabel(f"Dummy Slider {i+1}", main)
        #     slider = QSlider(Qt.Horizontal, main)
        #     slider.valueChanged.connect(self.slider_callback)  # Connect the callback to valueChanged signal
        #     self.sliders.append(slider)
        #     grouped_layout.addWidget(lbl)
        #     grouped_layout.addWidget(slider)

        # Add the grouped layout to settings layout
        settings_layout.addLayout(grouped_layout)

        # Push the remaining space to the bottom
        settings_layout.addStretch()

        self.webCamLayoutView.addLayout(settings_layout)
        self.webCamWidget.setLayout(self.webCamLayoutView)

    def updateWebcamFrame(self, pixmap, triggered_roi_index):
        self.webcam_roi_region.set_image(pixmap)
        self.webcam_roi_region.set_collision(triggered_roi_index)

    @Slot(bool)
    def edit_button_callback(self, state):
        print(f"Edit button state changed to: {state}")
        self.webcam_roi_region.setEditState(state)

    @Slot(int)
    def on_select_mp_model(self, index):
        selected_text = self.mp_model_combo_box.currentText()
        log.debug(f"Selected model: {selected_text}")
        self.mp_model_changed.emit(index)

    @Slot(int)
    def on_select_camsource(self, index):
        self._cam_index = index
        self.cam_index_changed.emit(self._cam_index)

    @Slot(int)
    def on_select_mouse_ctrl_mode(self, index):
        mouse_ctrl_mode = self.mouse_ctrl_mode_ui.currentText()
        self.mouse_ctrl_mode_changed.emit(index)

    @Slot(bool)
    def process_callback(self, state):
        self.process_state_changed.emit(state)

    @Slot(bool)
    def tracking_callback(self, state):
        self.tracking_state_changed.emit(state)

    def toggle_tracking(self):
        # TODO: change implementation, that a mouse operation like (move cursor, left click, right click) can only be mapped from one view (configuration)
        current_state = self.tracking_button.isChecked()
        self.tracking_button.setChecked(not current_state)
        self.tracking_state_changed.emit(not current_state)

    def slider_callback(self, value):
        sender = self.sender()  # Find out which slider sent the signal
        index = self.sliders.index(sender) + 1  # Get the slider number (1-based)
        log.debug(f"Slider {index} value changed to: {value}")

    @Slot(QRect)
    def on_new_roi_added(self, roi):
        self.roi_changed.emit(roi)


class MediaPipeApp(QMainWindow):
    def __init__(self, app, video_manager):
        super().__init__()
        self.app = app  # Store the QApplication reference here
        self.video_manager = video_manager

        self.setWindowTitle("CTRLABILITY")
        self.setupMenuBar()

        # Create the QTabWidget
        self.tab_widget = QTabWidget()

        # First tab for Video Processing
        tab1 = QWidget()
        tab1_layout = QVBoxLayout(tab1)
        self.webcam_tab_view1 = WebCamTabView(self, self.video_manager)
        tab1_layout.addWidget(self.webcam_tab_view1.webCamWidget)
        self.tab_widget.addTab(tab1, "Video Processing 1")

        # Second tab for Video Processing
        tab2 = QWidget()
        tab2_layout = QVBoxLayout(tab2)
        self.webcam_tab_view2 = WebCamTabView(self, self.video_manager)
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
        self.worker1 = MediaPipeThread(self.video_manager, 0, name="mp_thread1")
        self.worker1.moveToThread(self.thread1)
        self.setup_connections(self.thread1, self.worker1)

        self.thread2 = QThread()
        self.worker2 = MediaPipeThread(self.video_manager, 0, name="mp_thread2")
        self.worker2.moveToThread(self.thread2)
        self.setup_connections(self.thread2, self.worker2)

        self.thread1.start()
        self.thread2.start()

        # call cam1_changed when cam_index_changed signal is emitted
        self.webcam_tab_view1.cam_index_changed.connect(self.cam1_changed)
        # call cam2_changed when cam_index_changed signal is emitted
        self.webcam_tab_view2.cam_index_changed.connect(self.cam2_changed)

        # call cam1_resolution_changed when cam_resolution_index_changed signal is emitted
        self.webcam_tab_view1.mouse_ctrl_mode_changed.connect(self.view1_mouse_ctrl_mode_changed)
        # all cam2_resolution_changed when cam_resolution_index_changed signal is emitted
        self.webcam_tab_view2.mouse_ctrl_mode_changed.connect(self.view2_mouse_ctrl_mode_changed)

        # call tracking_state1_changed when tracking_state_changed signal is emitted
        self.webcam_tab_view1.tracking_state_changed.connect(self.tracking_state1_changed)
        # call tracking_state2_changed when tracking_state_changed signal is emitted
        self.webcam_tab_view2.tracking_state_changed.connect(self.tracking_state2_changed)

        # call process_state1_changed when process_state_changed signal is emitted
        self.webcam_tab_view1.process_state_changed.connect(self.process_state1_changed)
        # call process_state2_changed when process_state_changed signal is emitted
        self.webcam_tab_view2.process_state_changed.connect(self.process_state2_changed)

        # call mp_model1_changed when mp_model_changed signal is emitted
        self.webcam_tab_view1.mp_model_changed.connect(self.mp_model1_changed)
        # call mp_model2_changed when mp_model_changed signal is emitted
        self.webcam_tab_view2.mp_model_changed.connect(self.mp_model2_changed)

        # call roi1_changed when roi_changed signal is emitted
        self.webcam_tab_view1.roi_changed.connect(self.roi1_changed)
        # call roi2_changed when roi_changed signal is emitted
        self.webcam_tab_view2.roi_changed.connect(self.roi2_changed)

        self.webcam_tab_view1.process_button.setChecked(True)
        self.worker1.resume()
        self.webcam_tab_view2.process_button.setChecked(False)
        self.worker2.pause()

    @Slot(QRect)
    def roi1_changed(self, roi):
        self.worker1.handle_add_roi(roi)

    @Slot(QRect)
    def roi2_changed(self, roi):
        self.worker2.handle_add_roi(roi)

    @Slot(int)
    def mp_model1_changed(self, index):
        name = self.webcam_tab_view1.mp_model_combo_box.currentText()
        self.worker1.handle_model_changed(name)

    @Slot(int)
    def mp_model2_changed(self, index):
        name = self.webcam_tab_view2.mp_model_combo_box.currentText()
        self.worker2.handle_model_changed(name)

    @Slot(int)
    def cam1_changed(self, index):
        if (
            index == self.webcam_tab_view2.webcam_combo_box.currentIndex()
            and self.webcam_tab_view2.process_button.isChecked() == True
        ):
            self.webcam_tab_view1.webcam_combo_box.setCurrentIndex(self.webcam_tab_view1.cam_index_last_selected)
            self.webcam_tab_view1.webcam_roi_region.set_msg("Camera already in use in other view.")
        else:
            self.webcam_tab_view1.cam_index_last_selected = index
            self.webcam_tab_view1.webcam_roi_region.set_msg("")
            self.worker1.handle_cam_index_change(index)

    @Slot(int)
    def cam2_changed(self, index):
        if (
            index == self.webcam_tab_view1.webcam_combo_box.currentIndex()
            and self.webcam_tab_view1.process_button.isChecked() == True
        ):
            self.webcam_tab_view2.webcam_combo_box.setCurrentIndex(self.webcam_tab_view2.cam_index_last_selected)
            self.webcam_tab_view2.webcam_roi_region.set_msg("Camera already in use in other view.")
        else:
            self.webcam_tab_view2.cam_index_last_selected = index
            self.worker2.handle_cam_index_change(index)

    @Slot(int)
    def view1_mouse_ctrl_mode_changed(self, index):
        mode = self.webcam_tab_view1.mouse_ctrl_mode_ui.currentText()
        self.worker1.handle_mouse_ctrl_mode_change(mode)

    @Slot(int)
    def view2_mouse_ctrl_mode_changed(self, index):
        mode = self.webcam_tab_view2.mouse_ctrl_mode_ui.currentText()
        self.worker2.handle_mouse_ctrl_mode_change(mode)

    @Slot(bool)
    def tracking_state1_changed(self, state):
        self.worker1.handle_tracking_state_change(state)

    @Slot(bool)
    def tracking_state2_changed(self, state):
        self.worker2.handle_tracking_state_change(state)

    @Slot(bool)
    def process_state1_changed(self, state):
        if (
            self.webcam_tab_view1.webcam_combo_box.currentIndex()
            == self.webcam_tab_view2.webcam_combo_box.currentIndex()
            and self.webcam_tab_view2.process_button.isChecked() == True
        ):
            self.webcam_tab_view1.webcam_roi_region.set_msg("Camera already in use in other view.")
            self.webcam_tab_view1.process_button.setChecked(False)

        elif state:
            self.worker1.resume()
        else:
            self.worker1.pause()

    @Slot(bool)
    def process_state2_changed(self, state):
        if (
            self.webcam_tab_view1.webcam_combo_box.currentIndex()
            == self.webcam_tab_view2.webcam_combo_box.currentIndex()
            and self.webcam_tab_view1.process_button.isChecked() == True
        ):
            self.webcam_tab_view2.webcam_roi_region.set_msg("Camera already in use in other view.")
            self.webcam_tab_view2.process_button.setChecked(False)

        elif state:
            self.worker2.resume()
        else:
            self.worker2.pause()

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
    def on_progress(self, qImg, triggered_roi_index):
        sender = self.sender()

        if sender == self.worker1:
            pixmap = QPixmap.fromImage(qImg)
            self.webcam_tab_view1.updateWebcamFrame(pixmap, triggered_roi_index)
        elif sender == self.worker2:
            pixmap = QPixmap.fromImage(qImg)
            self.webcam_tab_view2.updateWebcamFrame(pixmap, triggered_roi_index)

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
        self.worker1.terminate()
        self.worker2.terminate()

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

    video_manager = VideoManager()

    args = parse_arguments()
    if args.resolution == "MIN":
        video_manager.set_preferred_height(480)
    elif args.resolution == "MAX":
        video_manager.set_preferred_height(720)

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

    mainWin = MediaPipeApp(app, video_manager)
    mainWin.show()
    sys.exit(app.exec())
