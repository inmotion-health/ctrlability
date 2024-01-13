import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)


class HandLandmarkProcessing:
    def __init__(self, frame, hand_landmarks):
        self.frame = frame
        self.hand_landmarks = hand_landmarks

    def draw_landmarks(self):
        mp_drawing.draw_landmarks(
            self.frame,
            self.hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            landmark_drawing_spec=drawing_spec,
            connection_drawing_spec=drawing_spec,
        )
