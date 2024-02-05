import logging

from ctrlability.core import Trigger, bootstrapper
from ctrlability.core.data_types import LandmarkData

log = logging.getLogger(__name__)


@bootstrapper.add()
class RegionOfInterest(Trigger):
    """
    A trigger that detects when a landmark is within a region of interest. The region of interest is defined by a
    position and size. The trigger can be set to keep triggering as long as the landmark is within the region.

    Inputs:
        LandmarkData: The landmark data.

    Returns:
        dict: The triggered landmarks.

    Args:
        landmarks (list): The list of landmarks to be checked.
        position (tuple): The position of the region of interest in normalized coordinates.
        size (tuple): The size of the region of interest.
        keep_triggering (bool, optional): Whether the trigger should keep triggering as long as the landmark is within the region. Defaults to False.
    """

    def __init__(self, landmarks, position, size, keep_triggering=False):
        self.landmarks = landmarks
        self.position = position
        self.size = size
        self.keep_triggering = keep_triggering
        self.triggered = False

    def is_in_region(self, landmark):
        """
        Checks if a landmark is within the region of interest.
        """
        if not landmark:  # if landmark does not exist
            return False

        (x, y) = (landmark.x, landmark.y)
        (pos_x, pos_y) = self.position
        (width, height) = self.size
        return pos_x <= x <= (pos_x + width) and pos_y <= y <= (pos_y + height)

    def check(self, landmark_data: LandmarkData) -> dict | None:
        if landmark_data is None:
            return

        if landmark_data.landmarks and not (self.triggered and not self.keep_triggering):
            triggered_landmarks = []

            for landmark_id in self.landmarks:
                landmark = landmark_data.landmarks[landmark_id]

                if self.is_in_region(landmark):
                    triggered_landmarks.append(landmark_id)

            if len(triggered_landmarks) > 0:
                self.triggered = True
                return {"triggered_landmarks": triggered_landmarks}
            else:
                self.triggered = False

    def __repr__(self):
        return f"RegionOfInterest(position = {self.position}, size = {self.size}, keep_triggering = {self.keep_triggering})"
