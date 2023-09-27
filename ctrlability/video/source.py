from typing import Optional, Tuple
import cv2
import imageio
import logging as log
import numpy as np
from ctrlability.video.source_resolution_provider import find_best_resolution

DEFAULT_RESOLUTION = (1280, 720)
DEFAULT_FPS = 30


class VideoSource:
    def __init__(self, camera_id: int, width: int, height: int):
        self.reader = None
        self.width = width
        self.height = height
        self.change_camera(camera_id)

    def __iter__(self):
        return self

    def __next__(self) -> np.array:
        frame = self.reader.get_next_data()

        if frame is None:
            raise StopIteration

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
        resolution, fps = find_best_resolution(camera_id) or (DEFAULT_RESOLUTION, DEFAULT_FPS)

        log.info(f"Using resolution {resolution} and FPS: {fps} for camera {camera_id}.")

        self.reader = imageio.get_reader(
            f"<video{camera_id}>",
            size=resolution,
            input_params=[
                "-framerate",
                f"{fps}",
            ],
        )
