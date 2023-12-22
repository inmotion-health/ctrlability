import math

import cv2
import mediapipe as mp
from vidcontrol import VideoManager

from mapping_engine import *

ConfigParser.CONFIG_PATH = "refactor_config.yaml"
b = Bootstrapper()

# TODO: where can we put the cursor tracking in there nicely?
#       if we want to have it as an action we need two things:
#       - a way to pass arbitrary data to the action
#       - a way to force the single use of a action in the config

# TODO: biggest remaining task is to be able to change settings dynamically, e.g. through the UI and a way to persist
#       these changes to "the" or "a" config.

# TODO: maybe enforce some kind of typing of the kind of data begin transferred from block to block


@b.add("VideoStream")
class VideoStream(Stream):
    def __init__(self, webcam_id):
        self.webcam_id = webcam_id

        self.video_manager = VideoManager()

        self.source = self.video_manager.get_video_source(webcam_id)
        self.source.set_mirror_frame(True)
        self.source.set_color_format("bgr")

    def get_next(self):
        frame = next(self.source)

        cv2.imshow("frame", frame)

        # TODO: observation
        #       here we could dig a tunnel with qt threads to the UI to pass along the current frame, though this is not
        #       good.how can we do this gracefully?
        #       we also would somehow need to build a mechanism that allows overlaying of info onto the frame.
        #       maybe we also could not do this and just keep this app in its final version in the background; though,
        #       for roi-processing, it is very helpful to be able to see stuff.

        return frame


@b.add("FaceLandmarkProcessor")
class FaceLandmarkProcessor(Processor):
    def __init__(self, mapping_engine: MappingEngine):
        super().__init__(mapping_engine)

        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            min_detection_confidence=0.5, min_tracking_confidence=0.5, static_image_mode=False, max_num_faces=1
        )

    def compute(self, data):
        results = self.face_mesh.process(data)

        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            return face_landmarks


def distance_between_points(a, b):
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)


@b.add("LandmarkDistance")
class LandmarkDistance(Trigger):
    def __init__(self, landmark1, landmark2, threshold):
        self.landmark1 = landmark1
        self.landmark2 = landmark2
        self.threshold = threshold

        print(f"landmarks: [{self.landmark1}, {self.landmark2}]")

    def check(self, data) -> bool:
        landmark1_coords = data.landmark[self.landmark1]
        landmark2_coords = data.landmark[self.landmark2]

        distance = distance_between_points(landmark1_coords, landmark2_coords)

        if distance > self.threshold:
            return True


@b.add("MouseAction")
class MouseAction(Action):
    def __init__(self, key_name):
        self.key = key_name

    def execute(self, **kwargs):
        print(f"triggered: {self.key}")


if __name__ == "__main__":
    streams = b.bootstrap()
    print(streams)

    while True:
        for stream in streams:
            stream.process(None)

        key = cv2.waitKey(1)  # Wait for 1 millisecond
        if key == 27:  # Exit loop on 'Esc' key press
            break

    cv2.destroyAllWindows()
