import logging as log
from typing import Optional, Set

import cv2
import imageio
import numpy as np

from ctrlability.video.vidplatform import video_platform
import platform

DEFAULT_RESOLUTION = (1280, 720)
DEFAULT_FPS = 30


class VideoSource:
    used_camera_ids: Set[int] = set()

    def __init__(self, camera_id: int, width: int, height: int):
        self.fps = None
        self.reader = None
        self.width = width
        self.height = height
        self._camera_id = camera_id
        self.change_camera(camera_id)

    def __iter__(self):
        return self

    def __next__(self) -> np.array:
        if not self.reader:
            return

        frame = self.reader.get_next_data()
        return self.flip(frame)

    @staticmethod
    def flip(frame: np.array) -> np.array:
        return cv2.flip(frame, 1)

    def close(self):
        if self.reader:
            self.reader = None
            VideoSource.used_camera_ids.remove(self._camera_id)

    def __del__(self):
        self.close()

    # FIXME: this is a mess
    #       - on macos when switching from <video2> to <video1> we get <video0> as the device but with the name of <video1>
    #       - switching cameras leads to weird behaviour for detection of already in use cameras
    # -> maybe we should keep a reference to all the open readers, their ID and count the references to them?
    def change_camera(self, camera_id: int):
        self.close()
        log.debug(f"Webcams currently in use: {VideoSource.used_camera_ids}")

        resolution, self.fps = video_platform.get_resolution_for(camera_id) or (DEFAULT_RESOLUTION, DEFAULT_FPS)

        self._camera_id = camera_id
        self.width = resolution[0]
        self.height = resolution[1]

        device_name = video_platform.get_ffmpeg_device_name(self._camera_id)
        log.info(f"Using resolution {resolution} and FPS: {self.fps} for camera with name: '{device_name}'")

        if platform.system() == "Windows":
            if camera_id in VideoSource.used_camera_ids:
                log.error(f"Camera with id {camera_id} is already in use!")
                self.reader = None
                return

        self.reader = imageio.get_reader(
            device_name,
            size=resolution,
            input_params=[
                "-framerate",
                f"{self.fps}",
            ],
        )

        VideoSource.used_camera_ids.add(camera_id)

    def change_resolution(self, cam_id):  # FIXME: big big smelly smell that we do this twice...
        resolutions = video_platform.list_available_resolutions(self._camera_id)
        selected_resolution = resolutions[cam_id]
        device_name = video_platform.get_ffmpeg_device_name(self._camera_id)

        log.info(f"Using resolution {selected_resolution}, FPS: {self.fps} for camera {device_name}.")

        self.reader = imageio.get_reader(
            device_name,
            size=(selected_resolution[0][0], selected_resolution[0][1]),
            input_params=["-framerate", f"{self.fps}", "-pix_fmt", "uyvy422"],
        )

    def get_probe_frame(self) -> Optional[np.array]:
        if not self.reader:
            log.error("probe frame: No reader found!")
            return None

        frame = self.reader.get_next_data()
        return self.flip(frame)
