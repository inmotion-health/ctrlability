from ctrlability.landmark_processing.face import FaceLandmarkProcessing
from ctrlability.video.source import VideoSource
from ctrlability.mousectrl import MouseCtrl
from PySide6.QtCore import Signal, QObject, Slot
from PySide6.QtGui import QImage
import mediapipe as mp
import time
import logging as log


class MediaPipeThread(QObject):
    started = Signal()
    finished = Signal()
    signalFrame = Signal(QImage)

    def __init__(self, camera_id=0):
        super().__init__()
        self.camera_id = camera_id
        self.webcam_source = VideoSource(camera_id, 1280, 720)

        # local state variables
        self.is_keeping_mouth_open = False

    def change_camera(self, camera_id):
        self.camera_id = camera_id
        self.webcam_source.change_camera(camera_id)

    def process(self):
        self.started.emit()

        with mp.solutions.holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
            for frame_rgb in self.webcam_source:
                results = holistic.process(frame_rgb)

                if results.face_landmarks is not None:
                    face = FaceLandmarkProcessing(frame_rgb, results.face_landmarks)
                    face.draw_landmarks()  # TODO: refactor drawing out of landmark processing

                    if MouseCtrl.is_tracking_enabled:
                        self.handle_mouse_events(face)

                height, width, channel = frame_rgb.shape
                bytesPerLine = 3 * width
                qImg = QImage(frame_rgb.data, width, height, bytesPerLine, QImage.Format_RGB888)

                self.signalFrame.emit(qImg)
        self.finished.emit()

    def handle_mouse_events(self, face):
        if not MouseCtrl.is_mouse_frozen:
            MouseCtrl.move_mouse(face.get_direction())

        if face.is_mouth_open():
            current_time = time.time() * 1000  # convert to ms

            # lets freeze the mouse position when the mouth is open to prevent
            # accidental mouse movement
            MouseCtrl.freeze_mouse_pos()

            first_time_open = self.is_keeping_mouth_open == False and MouseCtrl.get_left_clicks() == 0
            if first_time_open:
                MouseCtrl.left_click()
                self.is_keeping_mouth_open = True

            mouth_open_time = current_time - MouseCtrl.last_left_click_ms
            is_long_open = mouth_open_time > 500
            is_already_clicked = MouseCtrl.left_click_count == 1
            log.debug(
                f"Mouth open time: {mouth_open_time}ms, is_long_open: {is_long_open}, is_already_clicked: {is_already_clicked}"
            )
            if is_long_open and is_already_clicked:
                MouseCtrl.double_click()
                MouseCtrl.release_left_click()
        else:
            self.is_keeping_mouth_open = False
            MouseCtrl.unfreeze_mouse_pos()
            MouseCtrl.release_left_click()

        if face.is_mouth_small():
            is_already_right_clicked = MouseCtrl.is_right_mouse_clicked == True
            if not is_already_right_clicked:
                MouseCtrl.right_click()
        else:
            MouseCtrl.release_right_click()

    def handle_cam_index_change(self, camera_id):
        self.camera_id = camera_id
        self.webcam_source.change_camera(camera_id)
