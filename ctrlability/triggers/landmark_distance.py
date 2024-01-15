import logging

from ctrlability.core import Trigger, bootstrapper
from ctrlability.math.geometry import distance_between_points

log = logging.getLogger(__name__)


@bootstrapper.add()
class LandmarkDistance(Trigger):
    def __init__(self, landmark1, landmark2, threshold):
        self.landmark1 = landmark1
        self.landmark2 = landmark2
        self.threshold = threshold

        log.debug(f"setup landmark distance trigger: {self.landmark1} {self.landmark2} {self.threshold}")

    def check(self, data) -> dict | None:
        if data:
            landmark1_coords = data.landmark[self.landmark1]
            landmark2_coords = data.landmark[self.landmark2]

            distance = distance_between_points(landmark1_coords, landmark2_coords)

            if distance > self.threshold:
                return {"distance": distance, "length": 10}

    def __repr__(self):
        return f"LandmarkDistance(landmarks: [{self.landmark1}, {self.landmark2}])"
