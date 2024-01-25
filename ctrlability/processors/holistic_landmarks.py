import mediapipe as mp

from ctrlability.core import Processor, MappingEngine, bootstrapper
from ctrlability.core.data_types import FrameData, LandmarkData


@bootstrapper.add()
class HolisticLandmarkProcessor(Processor):
    def __init__(self, mapping_engine: MappingEngine):
        super().__init__(mapping_engine)

        self.holistic_mesh = mp.solutions.holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    def compute(self, data: FrameData):
        results = self.holistic_mesh.process(data.frame)

        return [
            LandmarkData(results.pose_landmarks.landmark, data.width, data.height),
            LandmarkData(results.left_hand_landmarks.landmark, data.width, data.height),
            LandmarkData(results.right_hand_landmarks.landmark, data.width, data.height),
            LandmarkData(results.face_landmarks.landmark, data.width, data.height),
        ]
