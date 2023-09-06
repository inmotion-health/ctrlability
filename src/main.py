import mediapipe as mp
from videosource import WebcamSource
import pyautogui
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic
mp_face_mesh_connections = mp.solutions.face_mesh_connections
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=3)


def add_landmarks_to_frame(frame, results):
    mp_drawing.draw_landmarks(
        frame,
        results.face_landmarks,
        connections=mp_face_mesh_connections.FACEMESH_TESSELATION,
        landmark_drawing_spec=drawing_spec,
        connection_drawing_spec=drawing_spec,
    )
    mp_drawing.draw_landmarks(
        frame,
        results.left_hand_landmarks,
        mp_holistic.HAND_CONNECTIONS,
        landmark_drawing_spec=drawing_spec,
        connection_drawing_spec=drawing_spec,
    )
    mp_drawing.draw_landmarks(
        frame,
        results.right_hand_landmarks,
        mp_holistic.HAND_CONNECTIONS,
        landmark_drawing_spec=drawing_spec,
        connection_drawing_spec=drawing_spec,
    )
    mp_drawing.draw_landmarks(
        frame,
        results.pose_landmarks,
        mp_holistic.POSE_CONNECTIONS,
        landmark_drawing_spec=drawing_spec,
        connection_drawing_spec=drawing_spec,
    )


def get_distances(results):
    left_ear = results.face_landmarks.landmark[93]
    right_ear = results.face_landmarks.landmark[323]
    head_top = results.face_landmarks.landmark[10]
    head_bottom = results.face_landmarks.landmark[152]

    nose = results.face_landmarks.landmark[4]

    head_width = abs(left_ear.x - right_ear.x)
    head_height = abs(head_top.y - head_bottom.y)

    distance_left = (nose.x - left_ear.x) / head_width
    distance_bottom = -1 * (nose.y - head_bottom.y) / head_height

    return distance_left, distance_bottom


def get_direction(results):
    distance_left, distance_bottom = get_distances(results)

    # threshold for the distance to the center of the screen after which the mouse will move
    X_THRESHOLD = 0.05
    Y_THRESHOLD = 0.03

    # normalize the distance to the center of the screen
    x_pos = (distance_left - 0.5) * 2
    y_pos = (distance_bottom - 0.5) * 2

    vec = [x_pos, y_pos]

    mouse_can_move = abs(x_pos) > X_THRESHOLD or abs(y_pos) > Y_THRESHOLD

    if mouse_can_move:
        return vec


def move_mouse(vec):
    if vec is None:
        return
    screen_width, screen_height = pyautogui.size()

    # scale the vector to a cubic function for smoother movement
    log_vec = np.power(np.array(vec), 3)

    # TODO: use size of current screen to avoid problems with multiple monitors
    log_vec *= screen_height

    # we need to compensate for a higher velocity in the y direction
    VELOCITY_COMPENSATION = 4

    v_x = log_vec[0]
    v_y = -1 * log_vec[1] * VELOCITY_COMPENSATION  # y is inverted

    # TODO: don't cross the screen border
    pyautogui.moveRel(v_x, v_y, duration=0.1)


def main():
    source = WebcamSource()

    with mp_holistic.Holistic(
        min_detection_confidence=0.5, min_tracking_confidence=0.5
    ) as holistic:
        for idx, (frame, frame_rgb) in enumerate(source):
            results = holistic.process(frame_rgb)

            values_exist = (
                results.face_landmarks is not None
                and results.pose_landmarks is not None
            )

            if values_exist:
                vec = get_direction(results)
                move_mouse(vec)

            add_landmarks_to_frame(frame, results)

            source.show(frame)


if __name__ == "__main__":
    main()
