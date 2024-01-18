import mediapipe as mp

from ctrlability.core import Processor, MappingEngine, bootstrapper


@bootstrapper.add()
class HandLandmarkProcessor(Processor):
    def __init__(self, mapping_engine: MappingEngine):
        super().__init__(mapping_engine)

        self.hand_mesh = mp.solutions.hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    def compute(self, data):
        results = self.hand_mesh.process(data)

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            return hand_landmarks
