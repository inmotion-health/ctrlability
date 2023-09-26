import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils

mp_face_mesh_connections = mp.solutions.face_mesh_connections
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)


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
            return False

    def is_mouth_small(self):
        distance = (self.mouth_right.x - self.mouth_left.x) / self.head_width
        if distance < 0.32:
            return True
        else:
            return False
