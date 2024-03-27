import logging
import subprocess

import cv2
from vidcontrol import VideoManager

from ctrlability.core import bootstrapper, Stream
from ctrlability.core.data_types import FrameData
from ctrlability.helpers.video_manager import video_manager

log = logging.getLogger(__name__)


def check_ffmpeg():
    import os 
    import sys
    import shutil
    print(os.getcwd())
    current_path = os.getcwd()
    error_log = f"{current_path}/error.log"
    meipass = sys._MEIPASS
    try:
        subprocess.check_output(["ffmpeg", "-version"])
    except Exception as e:
        with open(error_log, "a") as f:
            f.write(f"error while checking ffmpeg\n")
            f.write(f"Error: {str(e)}\n")
            f.write(f"PATH: {str(os.environ['PATH'])}\n")
            f.write(f"meipass: {sys._MEIPASS}\n")
            f.write(f"ffmpeg exist {os.path.exists(os.path.join(meipass,'lib','ffmpeg.exe'))}\n")
            f.write(f"ffmpeg path: {shutil.which('ffmpeg')}\n")
            f.write(f"ffmpeg path: {shutil.which('ffmpeg')}\n")
        raise RuntimeError("ffmpeg not found. Please install ffmpeg and add it to your PATH.")
    


@bootstrapper.add()
class VideoStream(Stream):
    """
    A Stream that captures video from a webcam. It returns the frame from the video stream. Uses vidcontrol for video
    capture, which uses ffmpeg.

    Returns:
        FrameData: The frame from the video stream.

    Args:
        webcam_id (int): The ID of the webcam.
        mirror (bool, optional): Whether to mirror the video stream. Defaults to True.
        mirror_horizontal (bool, optional): Whether to horizontally flip the video stream. Defaults to False.
        debug (bool, optional): Whether to enable debug mode. Defaults to False.
    """

    def __init__(self, webcam_id, mirror=True, mirror_horizontal=False, debug=False):
        self.webcam_id = webcam_id
        self.debug = debug

        #BUG: This check is somehow broken wehn building the app
        check_ffmpeg()
       

        self.source = video_manager.get_video_source(webcam_id)
        self.source.set_mirror_frame(mirror)
        self.source.set_flip_frame_horizontal(mirror_horizontal)

    def get_next(self):
        frame = next(self.source)

        if self.debug:
            cv2.imshow("VideoStream", frame)
            cv2.waitKey(1)

        return FrameData(frame, frame.shape[1], frame.shape[0])

    def __repr__(self):
        return f"VideoStream(webcam_id: {self.webcam_id})"
