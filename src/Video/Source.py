import cv2
import imageio
import logging as log

from Video.SourceResolutionProvider import find_best_resolution


class VideoSource:
    def __init__(self, camera_id, width, height):
        self.reader = None
        self.width = width
        self.height = height

        self.change_camera(camera_id)

    def __iter__(self):
        return self

    def __next__(self):
        frame = self.reader.get_next_data()

        if frame is None:
            raise StopIteration

        frame = self.flip(frame)

        return frame

    def flip(self, frame):
        return cv2.flip(frame, 1)

    def __del__(self):
        self.reader.close()

    def change_camera(self, camera_id):
        self._camera_id = camera_id
        resolution, fps = find_best_resolution(camera_id)

        if resolution is None:  # Fallback to 720p @ 30 FPS, which is the default for most webcams
            resolution = ((1280, 720), 30)

        log.info(f"Using resolution {resolution} and FPS: {fps} for camera {camera_id}.")

        # let's pass the framerate directly to ffmpeg to avoid issues with higher frame-rates on macOS
        self.reader = imageio.get_reader(
            f"<video{camera_id}>",
            size=(resolution[0], resolution[1]),
            input_params=[
                "-framerate",
                f"{fps}",
            ],
        )
