import mediapipe as mp
from videosource import WebcamSource
import pyautogui
import numpy as np

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.0
pyautogui.DARWIN_CATCH_UP_TIME = 0.0


mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic
mp_face_mesh_connections = mp.solutions.face_mesh_connections
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=3)


class MouseCtrl:
    def __init__(self):
        self._screen_width, self._screen_height = pyautogui.size()
        self._screen_center = (self._screen_width / 2, self._screen_height / 2)

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

            v_x = log_vec[0]
            v_y = -1 * log_vec[1] * VELOCITY_COMPENSATION  # y is inverted

            # TODO: don't cross the screen border
            pyautogui.moveRel(v_x, v_y, duration=0.1)

    def left_click(self):
        pyautogui.click()

    def right_click(self):
        pyautogui.rightClick()


class FaceLandmarkProcessing:
    def __init__(self, frame, face_landmarks):
        self.frame = frame
        self.face_landmarks = face_landmarks

        self.left_ear = face_landmarks.landmark[93]
        self.right_ear = face_landmarks.landmark[323]
        self.head_top = face_landmarks.landmark[10]
        self.head_bottom = face_landmarks.landmark[152]
        self.mouth_top = face_landmarks.landmark[12]
        self.mouth_bottom = face_landmarks.landmark[15]
        self.eye_brow_center = face_landmarks.landmark[9]

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

    def get_mouth_open(self):
        distance = (self.mouth_bottom.y - self.mouth_top.y) / self.head_height
        if distance > 0.08:
            return True
        else:
            return False

    def get_eye_brow_up(self):
        distance = (self.eye_brow_center.y - self.head_top.y) / self.head_height
        return distance


def main():
    source = WebcamSource()
    mouseCtrl = MouseCtrl()

    with mp_holistic.Holistic(
        min_detection_confidence=0.5, min_tracking_confidence=0.5
    ) as holistic:
        for idx, (frame, frame_rgb) in enumerate(source):
            results = holistic.process(frame_rgb)

            if results.face_landmarks is not None:
                face = FaceLandmarkProcessing(frame, results.face_landmarks)
                face.draw_landmarks()
                mouseCtrl.move_mouse(face.get_direction())

                if face.get_mouth_open():
                    print("Mouth Open")
                    mouseCtrl.left_click()
                # TODO Right Click
                # print (face.get_eye_brow_up())
            source.show(frame)


if __name__ == "__main__":
    main()
