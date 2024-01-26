import mediapipe as mp

from ctrlability.core import Processor, MappingEngine, bootstrapper
from ctrlability.core.data_types import FrameData, LandmarkData


@bootstrapper.add()
class FaceLandmarkProcessor(Processor):
    def __init__(self, mapping_engine: MappingEngine):
        super().__init__(mapping_engine)

        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            min_detection_confidence=0.5, min_tracking_confidence=0.5, static_image_mode=False, max_num_faces=1
        )

    def compute(self, data: FrameData):
        results = self.face_mesh.process(data.frame)

        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            return LandmarkData(face_landmarks.landmark, data.width, data.height)
