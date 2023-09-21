import platform
import sys
import cv2
import mediapipe as mp
from PySide6.QtGui import (
    QImage,
    QPixmap,
    QKeySequence,
    QIcon,
    QShortcut,
    QAction,
)
from PySide6.QtCore import QTimer, QThread, Signal, Qt, Slot
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
)
from PySide6.QtGui import QGuiApplication
from qt_material import apply_stylesheet, list_themes

import pyautogui

from VideoSource import VideoSource
import VideoSourceProvider

if platform.system() == "Darwin":
    import macmouse
import numpy as np
import time
import platform

import imageio

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.0
pyautogui.DARWIN_CATCH_UP_TIME = 0.00


mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic
mp_face_mesh_connections = mp.solutions.face_mesh_connections
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)


class MouseCtrl:
    AUTO_MODE = False

    def __init__(self):
        self._screen_width, self._screen_height = pyautogui.size()
        self._screen_center = (self._screen_width / 2, self._screen_height / 2)
        self.mouse_left_clicks = 0
        self.freezed_mouse_pos = False
        self.right_mouse_clicked = False
        self.last_left_click_ms = 0

    def set_center(self):
        pyautogui.moveTo(self._screen_center[0], self._screen_center[1])

    def move_mouse(self, vec):
        if vec is None:
            return

        # threshold for the distance to the center of the screen after which the mouse will move
        X_THRESHOLD = 0.05
        Y_THRESHOLD = 0.03

        mouse_can_move = abs(vec[0]) > X_THRESHOLD or abs(vec[1]) > Y_THRESHOLD

        if mouse_can_move:
            # scale the vector to a cubic function for smoother movement
            log_vec = np.power(np.array(vec), 3)

            log_vec *= self._screen_height

            # we need to compensate for a higher velocity in the y direction
            VELOCITY_COMPENSATION_X = 0.5
            VELOCITY_COMPENSATION_Y = 5

            v_x = log_vec[0] * VELOCITY_COMPENSATION_X
            v_y = -1 * log_vec[1] * VELOCITY_COMPENSATION_Y  # y is inverted

            x, y = pyautogui.position()
            # Calculate the new position after the relative move
            new_x = x + v_x
            new_y = y + v_y

            # check if new position is on screen
            if 0 <= new_x < self._screen_width and 0 <= new_y < self._screen_height:
                pyautogui.moveRel(v_x, v_y)
            else:
                # Adjust new_x and new_y if they would be off screen
                if new_x < 0:
                    new_x = 0
                elif new_x >= self._screen_width:
                    new_x = self._screen_width - 1

                if new_y < 0:
                    new_y = 0
                elif new_y >= self._screen_height:
                    new_y = self._screen_height - 1

                # Move to the adjusted position with a smooth transition
                pyautogui.moveTo(new_x, new_y)

    def left_click(self):
        pyautogui.click()

    def double_click(self):
        if platform.system() == "Darwin":
            macmouse.double_click()
        else:
            pyautogui.doubleClick()

    def right_click(self):
        pyautogui.rightClick()
        self.right_mouse_clicked = True


class FaceLandmarkProcessing:
    mouth_open_state = False

    def __init__(self, frame, face_landmarks):
        self.frame = frame
        self.face_landmarks = face_landmarks

        self.left_ear = face_landmarks.landmark[93]
        self.right_ear = face_landmarks.landmark[323]
        self.head_top = face_landmarks.landmark[10]
        self.head_bottom = face_landmarks.landmark[152]
        self.mouth_top = face_landmarks.landmark[12]
        self.mouth_bottom = face_landmarks.landmark[15]
        self.mouth_left = face_landmarks.landmark[61]
        self.mouth_right = face_landmarks.landmark[291]
        # self.eye_brow_center = face_landmarks.landmark[9]

        self.nose = self.face_landmarks.landmark[4]

        self.head_width = abs(self.left_ear.x - self.right_ear.x)
        self.head_height = abs(self.head_top.y - self.head_bottom.y)

    def get_distances(self):
        distance_left = (self.nose.x - self.left_ear.x) / self.head_width
        distance_bottom = -1 * (self.nose.y - self.head_bottom.y) / self.head_height

        return distance_left, distance_bottom

    def get_direction(self):
        distance_left, distance_bottom = self.get_distances()

        # normalize the distance to the center of the screen
        x_pos = (distance_left - 0.5) * 2
        y_pos = (distance_bottom - 0.5) * 2

        vec = [x_pos, y_pos]

        return vec

    def draw_landmarks(self):
        mp_drawing.draw_landmarks(
            self.frame,
            self.face_landmarks,
            connections=mp_face_mesh_connections.FACEMESH_TESSELATION,
            landmark_drawing_spec=drawing_spec,
            connection_drawing_spec=drawing_spec,
        )

    def is_mouth_open(self):
        distance = (self.mouth_bottom.y - self.mouth_top.y) / self.head_height
        if distance > 0.1:
            return True
        else:
            FaceLandmarkProcessing.mouth_open_state = False
            return False

    def is_mouth_small(self):
        distance = (self.mouth_right.x - self.mouth_left.x) / self.head_width
        if distance < 0.32:
            return True
        else:
            return False


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
        print("Virtual Keyboard opened!")


class MediaPipeThread(QThread):
    signalFrame = Signal(QImage)

    def __init__(self, camera_id=0):
        super().__init__()
        self.camera_id = camera_id

        self.webcam_source = VideoSource(camera_id, 1280, 720)

    def run(self):
        holistic = mp.solutions.holistic.Holistic()

        self.mouseCtrl = MouseCtrl()
        self.mouseCtrl.last_left_click_ms = 0
        self.mouseCtrl.set_center()

        with mp_holistic.Holistic(
            min_detection_confidence=0.5, min_tracking_confidence=0.5
        ) as holistic:
            for frame_rgb in self.webcam_source:
                results = holistic.process(frame_rgb)

                if results.face_landmarks is not None:
                    face = FaceLandmarkProcessing(frame_rgb, results.face_landmarks)
                    face.draw_landmarks()

                    if MouseCtrl.AUTO_MODE == True:
                        if self.mouseCtrl.freezed_mouse_pos == False:
                            # mouseCtrl.check_mouse_on_screen()
                            self.mouseCtrl.move_mouse(face.get_direction())

                        if face.is_mouth_open():
                            current_time = time.time() * 1000  # convert to ms

                            if self.mouseCtrl.freezed_mouse_pos == False:
                                self.mouseCtrl.freezed_mouse_pos = True

                            if (
                                FaceLandmarkProcessing.mouth_open_state == False
                                and self.mouseCtrl.mouse_left_clicks == 0
                            ):
                                self.mouseCtrl.left_click()
                                self.mouseCtrl.last_left_click_ms = current_time
                                self.mouseCtrl.mouse_left_clicks = 1
                                FaceLandmarkProcessing.mouth_open_state = True

                            if (
                                FaceLandmarkProcessing.mouth_open_state == True
                                and self.mouseCtrl.mouse_left_clicks == 1
                                and (current_time - self.mouseCtrl.last_left_click_ms)
                                > 500
                            ):
                                self.mouseCtrl.double_click()
                                self.mouseCtrl.last_left_click_ms = time.time() * 1000
                                self.mouseCtrl.mouse_left_clicks = 0
                        else:
                            FaceLandmarkProcessing.mouth_open_state = False
                            self.mouseCtrl.mouse_left_clicks = 0
                            self.mouseCtrl.freezed_mouse_pos = False

                        if face.is_mouth_small():
                            if self.mouseCtrl.right_mouse_clicked == False:
                                self.mouseCtrl.right_click()
                        else:
                            self.mouseCtrl.right_mouse_clicked = False

                # source.show(frame)
                height, width, channel = frame_rgb.shape
                bytesPerLine = 3 * width
                qImg = QImage(
                    frame_rgb.data, width, height, bytesPerLine, QImage.Format_RGB888
                )

                self.signalFrame.emit(qImg)

        holistic.close()
        self.source.release()

    def change_camera(self, camera_id):
        self.camera_id = camera_id
        self.webcam_source.change_camera(camera_id)


class MediaPipeApp(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app  # Store the QApplication reference here

        self.setWindowTitle("CTRLABILITY")
        # Setup Menu Bar
        self.setupMenuBar()
        self.mouseCtrl = MouseCtrl()

        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout()

        # Webcam display area (equivalent to BorderLayout::Center)
        self.label = QLabel(self)
        main_layout.addWidget(self.label)

        # Settings area (equivalent to BorderLayout::East)
        settings_layout = QVBoxLayout()

        # Create a QVBoxLayout for the buttons, labels, and sliders
        grouped_layout = QVBoxLayout()

        # Create a QComboBox to liste the connected webcames
        self.webcam_combo_box = QComboBox(self)
        webcam_dict = VideoSourceProvider.get_available_vidsources()
        for key, value in webcam_dict.items():
            self.webcam_combo_box.addItem(value)
        self.webcam_combo_box.setFixedWidth(250)
        grouped_layout.addWidget(self.webcam_combo_box)

        # Connect the activated signal to our custom slot
        self.webcam_combo_box.currentIndexChanged.connect(self.on_select_camsource)

        # Create the checkbox
        self.tracking_checkbox = QCheckBox("Tracking", self)
        # Connect the checkbox's state change signal to the callback
        self.tracking_checkbox.stateChanged.connect(self.tracking_callback)
        grouped_layout.addWidget(self.tracking_checkbox)

        # Create a shortcut for the 'T' key
        self.shortcut = QShortcut(QKeySequence(Qt.Key_T), self)
        self.shortcut.activated.connect(self.toggle_tracking_by_shortcut)

        # Adding buttons to the grouped layout
        self.buttons = []
        for i in range(4):
            btn = QPushButton(f"Button {i+1}", self)
            self.buttons.append(btn)
            grouped_layout.addWidget(btn)

        # Adding labels and sliders just below the buttons
        self.sliders = []
        for i in range(4):
            lbl = QLabel(f"Slider {i+1}", self)
            slider = QSlider(Qt.Horizontal, self)
            slider.valueChanged.connect(
                self.slider_callback
            )  # Connect the callback to valueChanged signal
            self.sliders.append(slider)
            grouped_layout.addWidget(lbl)
            grouped_layout.addWidget(slider)

        # Add the grouped layout to settings layout
        settings_layout.addLayout(grouped_layout)

        # Push the remaining space to the bottom
        settings_layout.addStretch()

        main_layout.addLayout(settings_layout)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Use a QTimer to delay the centering by 2000 milliseconds
        QTimer.singleShot(2000, self.center_on_screen)

        # Start the MediaPipe processing thread.
        self.thread = MediaPipeThread()
        self.thread.signalFrame.connect(self.update_frame)
        self.thread.start()

    def setupMenuBar(self):
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)

        themeMenu = QMenu("Themes", self)
        menubar.addMenu(themeMenu)

        for theme in list_themes():
            themeMenu.addAction(
                theme, lambda theme_name=theme: self.applyTheme(theme_name)
            )

    def applyTheme(self, theme_name):
        apply_stylesheet(self.app, theme=theme_name)  # apply the chosen theme

    def center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()  # Get screen geometry
        window = self.geometry()  # Get window geometry
        self.move(
            (screen.width() - window.width()) / 2,
            (screen.height() - window.height()) / 2,
        )

    @Slot(int)
    def on_select_camsource(self, index):
        """Slot that is called when an item in the QComboBox is selected."""
        print(f"Selected index: {index}")
        self.thread.change_camera(index)

    def tracking_callback(self, state):
        if state == 0:
            print("Tracking is off.")
            MouseCtrl.AUTO_MODE = False

        elif state == 2:
            print("Tracking is on.")
            MouseCtrl.AUTO_MODE = True
            pyautogui.moveTo(pyautogui.size()[0] / 2, pyautogui.size()[1] / 2)

    def toggle_tracking_by_shortcut(self):
        current_state = self.tracking_checkbox.isChecked()
        self.tracking_checkbox.setChecked(not current_state)

    def slider_callback(self, value):
        sender = self.sender()  # Find out which slider sent the signal
        index = self.sliders.index(sender) + 1  # Get the slider number (1-based)
        print(f"Slider {index} value changed to: {value}")

    def update_frame(self, qImg):
        pixmap = QPixmap.fromImage(qImg)
        self.label.setPixmap(pixmap)

    def closeEvent(self, event):
        self.thread.terminate()
        event.accept()


if __name__ == "__main__":
    # ToDo: fix in deplyment: currently developlemt hack to show application name in menu bar
    if sys.platform == "darwin":
        from Foundation import NSBundle

        app_info = NSBundle.mainBundle().infoDictionary()
        app_info["CFBundleName"] = "CTRLABILITY"

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