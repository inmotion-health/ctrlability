from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.clock import Clock

from videosource import WebcamSource
import mediapipe as mp
import platform
import pyautogui
import macmouse
import numpy as np
import time
import libctrlability
import cv2

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.0
pyautogui.DARWIN_CATCH_UP_TIME = 0.00

mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic
mp_face_mesh_connections = mp.solutions.face_mesh_connections
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=3)


class MouseCtrl:
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
            VELOCITY_COMPENSATION = 4

            v_x = log_vec[0] * VELOCITY_COMPENSATION
            v_y = -1 * log_vec[1] * VELOCITY_COMPENSATION  # y is inverted

            # TODO: don't cross the screen border
            pyautogui.moveRel(v_x, v_y)

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


class MainApp(App):
    def build(self):
        # Root layout
        root_layout = BoxLayout(orientation="horizontal")

        self.webcamView = Image()
        # Main view for webcam
        # webcam_label = Label(text="Webcam Stream Goes Here", size_hint=(0.75, 1))

        root_layout.add_widget(self.webcamView)

        # Settings layout
        settings_layout = BoxLayout(orientation="vertical", size_hint=(0.25, 1))

        # Adding 4 buttons
        for i in range(4):
            settings_layout.add_widget(Button(text=f"Setting {i+1}"))

        self.slider1 = Slider(min=0, max=10, value=4)
        self.slider1.bind(value=self.on_slider1_value)
        settings_layout.add_widget(Label(text="velocity x factor"))
        settings_layout.add_widget(self.slider1)

        self.slider2 = Slider(min=0, max=10, value=4)
        self.slider2.bind(value=self.on_slider2_value)
        settings_layout.add_widget(Label(text="velocity y factor"))
        settings_layout.add_widget(self.slider2)

        self.slider3 = Slider(min=0, max=1, value=0.1, step=0.01)
        self.slider3.bind(value=self.on_slider3_value)
        settings_layout.add_widget(Label(text="Dist is_mouth_open"))
        settings_layout.add_widget(self.slider3)

        self.slider4 = Slider(min=0, max=1, value=0.32, step=0.01)
        self.slider4.bind(value=self.on_slider4_value)
        settings_layout.add_widget(Label(text="Dist is_mouth_small"))
        settings_layout.add_widget(self.slider4)

        root_layout.add_widget(settings_layout)

        Clock.schedule_interval(self.update, 1.0 / 33.0)

        self.mouseCtrl = MouseCtrl()
        self.mouseCtrl.last_left_click_ms = 0
        self.mouseCtrl.set_center()
        self.source = WebcamSource()

        return root_layout

    def update(self, dt):
        # ret, frame = self.source.get_frame()
        frame, frame_rgb = next(self.source)

        with mp_holistic.Holistic(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        ) as holistic:
            if frame is not None:
                results = holistic.process(frame_rgb)

                if results.face_landmarks is not None:
                    face = FaceLandmarkProcessing(frame, results.face_landmarks)
                    face.draw_landmarks()

                    if self.mouseCtrl.freezed_mouse_pos == False:
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
                            and (current_time - self.mouseCtrl.last_left_click_ms) > 500
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

        # next(self.source)
        # frame = self.source.get_frame()
        frame = cv2.flip(frame, 0)  # vertically flip the image

        buf = frame.tostring()
        image_texture = Texture.create(
            size=(frame.shape[1], frame.shape[0]), colorfmt="bgr"
        )
        image_texture.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
        # Display the texture on the Image widget
        self.webcamView.texture = image_texture

    def on_slider1_value(self, instance, value):
        # Here you can adjust the VELOCITY_COMPENSATION X based on slider value
        pass  # Replace with your logic

    def on_slider2_value(self, instance, value):
        # Here you can adjust the VELOCITY_COMPENSATION Y based on slider value
        pass  # Replace with your logic

    def on_slider3_value(self, instance, value):
        # Here you can adjust the distance in is_mouth_open function based on slider value
        FaceLandmarkProcessing.MOUTH_OPEN_THRESHOLD = value

    def on_slider4_value(self, instance, value):
        # Here you can adjust the distance in is_mouth_small function based on slider value
        FaceLandmarkProcessing.MOUTH_SMALL_THRESHOLD = value


if __name__ == "__main__":
    MainApp().run()
