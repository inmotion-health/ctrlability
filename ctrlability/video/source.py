import logging as log

import cv2
import imageio
import numpy as np

from ctrlability.video.platform import platform

DEFAULT_RESOLUTION = (1280, 720)
DEFAULT_FPS = 30


class VideoSource:
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
        frame = self.reader.get_next_data()
        return self.flip(frame)

    @staticmethod
    def flip(frame: np.array) -> np.array:
        return cv2.flip(frame, 1)

    def close(self):
        if self.reader:
            self.reader.close()

    def __del__(self):
        self.close()

    def change_camera(self, camera_id: int):
        resolution, self.fps = platform.get_resolution_for(camera_id) or (DEFAULT_RESOLUTION, DEFAULT_FPS)

        log.info(f"Using resolution {resolution} and FPS: {self.fps} for camera {camera_id}.")

        self.reader = imageio.get_reader(
            f"<video{camera_id}>",
            size=resolution,
            input_params=[
                "-framerate",
                f"{self.fps}",
            ],
        )

    def change_resolution(self, cam_id):
        resolutions = platform.list_available_resolutions(self._camera_id)
        selected_resolution = resolutions[cam_id]

        log.info(f"Using resolution {selected_resolution}")

        self.reader = imageio.get_reader(
            f"<video{self._camera_id}>",
            size=(selected_resolution[0][0], selected_resolution[0][1]),
            input_params=["-framerate", f"{self.fps}", "-pix_fmt", "uyvy422"],
        )

    def get_probe_frame(self) -> np.array:
        frame = self.reader.get_next_data()
        return self.flip(frame)
