import mediapipe as mp
from videosource import WebcamSource
import platform
import pyautogui
import macmouse
import numpy as np
import time
import libctrlability


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
                pyautogui.moveTo(
                    new_x, new_y, duration=1, tween=pyautogui.easeInOutQuad
                )

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


def main():
    source = WebcamSource()
    mouseCtrl = MouseCtrl()

    mouseCtrl.last_left_click_ms = 0

    libctrlability.hello()

    mouseCtrl.set_center()

    with mp_holistic.Holistic(
        min_detection_confidence=0.5, min_tracking_confidence=0.5
    ) as holistic:
        for idx, (frame, frame_rgb) in enumerate(source):
            results = holistic.process(frame_rgb)

            if results.face_landmarks is not None:
                face = FaceLandmarkProcessing(frame, results.face_landmarks)
                face.draw_landmarks()

                if mouseCtrl.freezed_mouse_pos == False:
                    # mouseCtrl.check_mouse_on_screen()
                    mouseCtrl.move_mouse(face.get_direction())

                if face.is_mouth_open():
                    current_time = time.time() * 1000  # convert to ms

                    if mouseCtrl.freezed_mouse_pos == False:
                        mouseCtrl.freezed_mouse_pos = True

                    if (
                        FaceLandmarkProcessing.mouth_open_state == False
                        and mouseCtrl.mouse_left_clicks == 0
                    ):
                        mouseCtrl.left_click()
                        mouseCtrl.last_left_click_ms = current_time
                        mouseCtrl.mouse_left_clicks = 1
                        FaceLandmarkProcessing.mouth_open_state = True

                    if (
                        FaceLandmarkProcessing.mouth_open_state == True
                        and mouseCtrl.mouse_left_clicks == 1
                        and (current_time - mouseCtrl.last_left_click_ms) > 500
                    ):
                        mouseCtrl.double_click()
                        mouseCtrl.last_left_click_ms = time.time() * 1000
                        mouseCtrl.mouse_left_clicks = 0
                else:
                    FaceLandmarkProcessing.mouth_open_state = False
                    mouseCtrl.mouse_left_clicks = 0
                    mouseCtrl.freezed_mouse_pos = False

                if face.is_mouth_small():
                    if mouseCtrl.right_mouse_clicked == False:
                        mouseCtrl.right_click()
                else:
                    mouseCtrl.right_mouse_clicked = False

            source.show(frame)


if __name__ == "__main__":
    main()
