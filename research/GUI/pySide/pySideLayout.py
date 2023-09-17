# pip install PySide2
# pip install pyobjc-framework-Cocoa
# pip install qt-material
# pip install mediapipe
# pip install opencv-python

import sys
import cv2
import mediapipe as mp
from PySide2.QtWidgets import QApplication, QMainWindow, QLabel
from PySide2.QtGui import QImage, QPixmap
from PySide2.QtCore import QTimer, QThread, Signal, Qt
from PySide2.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QSlider,
    QWidget,
    QMenuBar,
    QMenu,
)
from PySide2.QtGui import QGuiApplication
from qt_material import apply_stylesheet, list_themes


mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic
mp_face_mesh_connections = mp.solutions.face_mesh_connections
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=3)


class MediaPipeThread(QThread):
    signalFrame = Signal(QImage)

    def run(self):
        cap = cv2.VideoCapture(0)
        holistic = mp.solutions.holistic.Holistic()

        while True:
            ret, image = cap.read()
            if not ret:
                break

            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = holistic.process(image_rgb)

            # Draw landmarks
            if results.face_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(
                    image_rgb,
                    results.face_landmarks,
                    connections=mp_face_mesh_connections.FACEMESH_TESSELATION,
                    landmark_drawing_spec=drawing_spec,
                    connection_drawing_spec=drawing_spec,
                )

            height, width, channel = image_rgb.shape
            bytesPerLine = 3 * width
            qImg = QImage(
                image_rgb.data, width, height, bytesPerLine, QImage.Format_RGB888
            )

            self.signalFrame.emit(qImg)

        holistic.close()
        cap.release()


class MediaPipeApp(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app  # Store the QApplication reference here

        self.setWindowTitle("CTRLABILITY")
        # Setup Menu Bar
        self.setupMenuBar()

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
    apply_stylesheet(app, theme="dark_teal.xml")

    mainWin = MediaPipeApp(app)
    mainWin.show()
    sys.exit(app.exec_())
