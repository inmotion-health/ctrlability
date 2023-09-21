import cv2
import imageio


class VideoSource:
    def __init__(self, camera_id, width, height):
        self._camera_id = camera_id
        self.width = width
        self.height = height

        self.reader = imageio.get_reader(f"<video{camera_id}>", size=(width, height))

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
        self.reader = imageio.get_reader(
            f"<video{camera_id}>", size=(self.width, self.height)
        )
