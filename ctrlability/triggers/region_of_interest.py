import logging

from ctrlability.core import Trigger, bootstrapper

log = logging.getLogger(__name__)


@bootstrapper.add()
class RegionOfInterest(Trigger):
    def __init__(self, landmarks, position, size, keep_triggering=False):
        self.landmarks = landmarks

        self.position = position
        self.size = size

        self.keep_triggering = keep_triggering

        self.triggered = False

    def is_in_region(self, landmark):
        if not landmark:  # if landmark does not exist
            return False

        (x, y) = (landmark.x, landmark.y)
        (pos_x, pos_y) = self.position
        (width, height) = self.size
        return pos_x <= x <= (pos_x + width) and pos_y <= y <= (pos_y + height)

    def check(self, data) -> dict | None:
        if data and not (self.triggered and not self.keep_triggering):
            triggered_landmarks = []

            for landmark_id in self.landmarks:
                landmark = data.landmark[landmark_id]

                if self.is_in_region(landmark):
                    triggered_landmarks.append(landmark_id)

            if len(triggered_landmarks) > 0:
                self.triggered = True
                return {"triggered_landmarks": triggered_landmarks}
            else:
                self.triggered = False

    def __repr__(self):
        return f"RegionOfInterest: position = {self.position}, size = {self.size}, keep_triggering = {self.keep_triggering}"
