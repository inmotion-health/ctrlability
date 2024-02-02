import mediapipe as mp

from ctrlability.core import Processor, MappingEngine, bootstrapper
from ctrlability.core.data_types import FrameData, LandmarkData


@bootstrapper.add()
class HolisticLandmarkProcessor(Processor):
    """
    A Processor that takes a frame and returns the landmarks detected in the frame. For details on the landmarks, see
    the images in the PoseLandmarkProcessor, HandLandmarkProcessor, and FaceLandmarkProcessor.

    To connect other nodes to this node, use a SignalDivider to split the output into two separate signals.

    Inputs:
        FrameData: The frame in which the landmarks should be detected.

    Returns:
        (LandmarkData, LandmarkData, LandmarkData, LandmarkData): The landmarks detected in the frame. The first element is the pose landmarks, the second element is the left hand landmarks, the third element is the right hand landmarks, and the fourth element is the face landmarks.
    """

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
