from FaceLandmarkProcessing import FaceLandmarkProcessing
from VideoSource import VideoSource
from MouseControl import MouseController
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage
import mediapipe as mp
import time


class MediaPipeThread(QThread):
    signalFrame = Signal(QImage)

    def __init__(self, camera_id=0):
        super().__init__()
        self.camera_id = camera_id

        self.webcam_source = VideoSource(camera_id, 1280, 720)

    def run(self):
        self.mouseCtrl = MouseController()
        self.mouseCtrl.last_left_click_ms = 0
        self.mouseCtrl.set_center()

        with mp.solutions.holistic.Holistic(
            min_detection_confidence=0.5, min_tracking_confidence=0.5
        ) as holistic:
            for frame_rgb in self.webcam_source:
                results = holistic.process(frame_rgb)

                if results.face_landmarks is not None:
                    face = FaceLandmarkProcessing(frame_rgb, results.face_landmarks)
                    face.draw_landmarks()

                    if MouseController.AUTO_MODE == True:
                        if self.mouseCtrl.frozen_mouse_pos == False:
                            self.mouseCtrl.move_mouse(face.get_direction())

                        if face.is_mouth_open():
                            current_time = time.time() * 1000  # convert to ms

                            if self.mouseCtrl.frozen_mouse_pos == False:
                                self.mouseCtrl.frozen_mouse_pos = True

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
                            self.mouseCtrl.frozen_mouse_pos = False

                        if face.is_mouth_small():
                            if self.mouseCtrl.right_mouse_clicked == False:
                                self.mouseCtrl.right_click()
                        else:
                            self.mouseCtrl.right_mouse_clicked = False

                height, width, channel = frame_rgb.shape
                bytesPerLine = 3 * width
                qImg = QImage(
                    frame_rgb.data, width, height, bytesPerLine, QImage.Format_RGB888
                )

                self.signalFrame.emit(qImg)

    def change_camera(self, camera_id):
        self.camera_id = camera_id
        self.webcam_source.change_camera(camera_id)
