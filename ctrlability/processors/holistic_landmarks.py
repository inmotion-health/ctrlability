import mediapipe as mp

from ctrlability.core import Processor, MappingEngine, bootstrapper


@bootstrapper.add()
class HolisticLandmarkProcessor(Processor):
    def __init__(self, mapping_engine: MappingEngine):
        super().__init__(mapping_engine)

        self.holistic_mesh = mp.solutions.holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    def compute(self, data):
        results = self.holistic_mesh.process(data)

        return (
            results.pose_landmarks.landmark,
            results.left_hand_landmarks.landmark,
            results.right_hand_landmarks.landmark,
            results.face_landmarks.landmark,
        )
