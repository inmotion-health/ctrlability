import mediapipe as mp

from ctrlability.core import Processor, MappingEngine, bootstrapper


@bootstrapper.add()
class PoseLandmarkProcessor(Processor):
    def __init__(self, mapping_engine: MappingEngine):
        super().__init__(mapping_engine)

        self.pose_mesh = mp.solutions.pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    def compute(self, data):
        results = self.pose_mesh.process(data)

        if results.pose_landmarks:
            pose_landmarks = results.pose_landmarks
            return pose_landmarks.landmark
