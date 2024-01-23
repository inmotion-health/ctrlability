import logging
import time

from ctrlability.core import Trigger, bootstrapper
from ctrlability.math.geometry import distance_between_points

log = logging.getLogger(__name__)


@bootstrapper.add()
class LandmarkDistance(Trigger):
    def __init__(self, landmark1, landmark2, threshold, timer=0.0):
        self.landmark1 = landmark1
        self.landmark2 = landmark2
        self.threshold = threshold
        self.timer = timer / 1000  # convert to seconds
        self.exceeded_time = 0.0
        self.triggered = False

        log.debug(f"setup landmark distance trigger: {self.landmark1} {self.landmark2} {self.threshold}")

    def check(self, data) -> dict | None:
        if data:
            landmark1_coords = data.landmark[self.landmark1]
            landmark2_coords = data.landmark[self.landmark2]

            distance = distance_between_points(landmark1_coords, landmark2_coords)

            if distance > self.threshold:
                if self.exceeded_time == 0.0:
                    self.exceeded_time = time.time()

                if time.time() - self.exceeded_time >= self.timer and not self.triggered:
                    self.exceeded_time = 0.0
                    self.triggered = True
                    return {"distance": distance, "state": self.exceeded_time}

            else:
                self.exceeded_time = 0.0
                self.triggered = False

    def __repr__(self):
        return f"LandmarkDistance(landmarks: [{self.landmark1}, {self.landmark2}])"
