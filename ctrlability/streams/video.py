import logging
import subprocess
import sys

from vidcontrol import VideoManager

from ctrlability.engine import bootstrapper, Stream

log = logging.getLogger(__name__)


def check_ffmpeg():
    try:
        subprocess.check_output(["ffmpeg", "-version"])
    except OSError:
        log.error("ffmpeg not found. Please install ffmpeg and add it to your PATH.")
        sys.exit(1)


@bootstrapper.add()
class VideoStream(Stream):
    def __init__(self, webcam_id, mirror=True, mirror_horizontal=False):
        self.webcam_id = webcam_id

        check_ffmpeg()

        self.video_manager = VideoManager()

        self.source = self.video_manager.get_video_source(webcam_id)
        self.source.set_mirror_frame(mirror)
        self.source.set_flip_frame_horizontal(mirror_horizontal)

    def get_next(self):
        frame = next(self.source)

        return frame
