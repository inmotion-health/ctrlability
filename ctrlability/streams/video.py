import logging
import subprocess

import cv2
from vidcontrol import VideoManager

from ctrlability.core import bootstrapper, Stream

log = logging.getLogger(__name__)


def check_ffmpeg():
    try:
        subprocess.check_output(["ffmpeg", "-version"])
    except OSError:
        raise RuntimeError("ffmpeg not found. Please install ffmpeg and add it to your PATH.")


@bootstrapper.add()
class VideoStream(Stream):
    def __init__(self, webcam_id, mirror=True, mirror_horizontal=False, debug=False):
        self.webcam_id = webcam_id
        self.debug = debug

        check_ffmpeg()

        self.video_manager = VideoManager()

        self.source = self.video_manager.get_video_source(webcam_id)
        self.source.set_mirror_frame(mirror)
        self.source.set_flip_frame_horizontal(mirror_horizontal)

    def get_next(self):
        frame = next(self.source)

        if self.debug:
            cv2.imshow("VideoStream", frame)
            cv2.waitKey(1)

        return frame

    def __repr__(self):
        return f"VideoStream(webcam_id: {self.webcam_id})"
