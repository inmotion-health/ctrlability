import mediapipe as mp

from ctrlability.core import Processor, MappingEngine, bootstrapper
from ctrlability.core.data_types import LandmarkData, FrameData


@bootstrapper.add()
class HandLandmarkProcessor(Processor):
    """
    A Processor that takes a frame and returns the landmarks detected in the frame. For details on the landmarks, see
    the image below.

    ![landmarks](img/hand_landmarks.png)

    Inputs:
        FrameData: The frame in which the landmarks should be detected.

    Returns:
        LandmarkData: The landmarks detected in the frame.
    """

    def __init__(self, mapping_engine: MappingEngine):
        super().__init__(mapping_engine)

        self.hand_mesh = mp.solutions.hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    def compute(self, data: FrameData):
        results = self.hand_mesh.process(data.frame)

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            return LandmarkData(hand_landmarks.landmark, data.width, data.height)
