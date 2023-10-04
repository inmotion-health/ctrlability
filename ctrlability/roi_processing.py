from PySide6.QtCore import QRect, QPoint


class RoiProcessing:
    def __init__(self, width, height):
        self.roi_list = []
        self.movable_roi_list = []  # from mediapipelandmarks
        self.width = width
        self.height = height

    def add_roi(self, roi):
        self.roi_list.append(roi)

    def check_collision(self, landmarks):
        points = self._convert_landmarks_to_points(landmarks)
        for index, roi in enumerate(self.roi_list):
            for pt in points:
                if roi.contains(pt):
                    return index
        return -1

    def _convert_landmarks_to_points(self, landmarks):
        """Convert MediaPipe hand landmarks to a list of QPoint."""
        return [QPoint(landmark.x * self.width, landmark.y * self.height) for landmark in landmarks.landmark]
