import cv2
import mediapipe as mp
import numpy as np

from kivy.app import App
from kivy.uix.pagelayout import PageLayout
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.uix.slider import Slider
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.clock import Clock

mp_face_mesh = mp.solutions.face_mesh


class WebcamApp(App):
    def build(self):
        layout = PageLayout()

        # First page: Webcam feed
        self.cam = cv2.VideoCapture(0)
        self.image = Image()
        layout.add_widget(self.image)

        # Second page: Settings
        settings_layout = PageLayout()
        settings_layout.add_widget(Slider(orientation="horizontal"))
        settings_layout.add_widget(Slider(orientation="horizontal"))
        settings_layout.add_widget(
            Button(text="Show Keyboard", on_press=self.show_keyboard)
        )
        settings_layout.add_widget(Button(text="Button 2"))
        layout.add_widget(settings_layout)

        # Schedule the update of the webcam feed
        Clock.schedule_interval(self.update, 1.0 / 33.0)

        return layout

    def show_keyboard(self, instance):
        Window.request_keyboard(self._keyboard_closed, self)

    def _keyboard_closed(self):
        pass

    def update(self, dt):
        ret, frame = self.cam.read()
        if not ret:
            return

        # Process the frame with Mediapipe Face Mesh
        with mp_face_mesh.FaceMesh(
            static_image_mode=True, max_num_faces=1, min_detection_confidence=0.2
        ) as face_mesh:
            results = face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            if results.multi_face_landmarks:
                for landmarks in results.multi_face_landmarks:
                    for _, landmark in enumerate(landmarks.landmark):
                        frame = cv2.circle(
                            frame,
                            (
                                int(landmark.x * frame.shape[1]),
                                int(landmark.y * frame.shape[0]),
                            ),
                            1,
                            (0, 255, 0),
                            1,
                        )

        # Convert the frame to texture
        buf1 = cv2.flip(frame, 0)
        buf = buf1.tostring()
        image_texture = Texture.create(
            size=(frame.shape[1], frame.shape[0]), colorfmt="bgr"
        )
        image_texture.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")

        # Display the texture on the Image widget
        self.image.texture = image_texture


if __name__ == "__main__":
    WebcamApp().run()
