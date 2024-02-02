import logging
import time

from ctrlability.core import Trigger, bootstrapper
from ctrlability.core.data_types import LandmarkData
from ctrlability.math.geometry import distance_between_points

log = logging.getLogger(__name__)


@bootstrapper.add()
class LandmarkDistance(Trigger):
    """
    The LandmarkDistance class is a subclass of Trigger and is used to check the distance between two landmarks.
    It triggers when the distance between the two landmarks exceeds a threshold.

    Args:
        landmarks: A list of two landmarks between which the distance should be checked.
        threshold: The threshold value for the distance between the landmarks.
        timer: The time duration (in milliseconds) for which the distance should exceed the threshold before triggering (default: 0.0).
        direction: The direction of the trigger. Can be "greater" or "smaller" (default: "greater").
        normalize: A boolean value to normalize the distance with respect to a reference distance (default: False).
        ref_landmarks: A list of two landmarks to be used as reference for normalizing the distance (default: None).
    """

    def __init__(self, landmarks, threshold, timer=0.0, direction="greater", normalize=False, ref_landmarks=None):
        if len(landmarks) != 2:
            raise ValueError("landmarks should be a list of two landmarks")

        if len(ref_landmarks) != 2:
            raise ValueError("ref_landmarks should be a list of two landmarks")

        self.landmark1 = landmarks[0]
        self.landmark2 = landmarks[1]
        self.threshold = threshold

        self.normalize = normalize
        self.ref_landmarks = ref_landmarks

        self.timer = timer / 1000  # convert to seconds
        self.exceeded_time = 0.0

        self.triggered = False  # used to prevent multiple triggers
        self.direction = direction

        self.valid_directions = ["greater", "smaller"]
        if direction not in self.valid_directions:
            raise ValueError(f"direction should be one of {self.valid_directions}")

        log.debug(f"setup landmark distance trigger: {self.landmark1} {self.landmark2} {self.threshold}")

    def check(self, data: LandmarkData) -> dict | None:
        if data:
            landmark1_coords = data.landmarks[self.landmark1]
            landmark2_coords = data.landmarks[self.landmark2]

            distance = distance_between_points(landmark1_coords, landmark2_coords)

            if self.normalize:
                ref_distance = distance_between_points(
                    data.landmarks[self.ref_landmarks[0]], data.landmarks[self.ref_landmarks[1]]
                )
                distance = distance / ref_distance

            condition_greater = distance > self.threshold
            condition_smaller = distance < self.threshold

            condition = condition_greater if self.direction == "greater" else condition_smaller

            if condition:
                if self.exceeded_time == 0.0:
                    self.exceeded_time = time.time()

                if time.time() - self.exceeded_time >= self.timer and not self.triggered:
                    self.exceeded_time = 0.0
                    self.triggered = True
                    log.debug(f"triggered landmark distance trigger: {self.landmark1} {self.landmark2} {distance}")
                    return {"distance": distance, "state": self.exceeded_time}

            else:
                self.exceeded_time = 0.0
                self.triggered = False

    def __repr__(self):
        return f"LandmarkDistance(landmarks: [{self.landmark1}, {self.landmark2}])"
