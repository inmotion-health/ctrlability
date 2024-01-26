import logging

import numpy as np
import pyautogui

from ctrlability.core import Trigger, bootstrapper
from ctrlability.core.data_types import LandmarkData
from ctrlability.helpers.mousectrl import MouseCtrl

log = logging.getLogger(__name__)


@bootstrapper.add()
class RelativeCursorControl(Trigger):
    def __init__(self, x_threshold=0.05, y_threshold=0.03, velocity_compensation_x=0.15, velocity_compensation_y=3.5):
        log.debug(f"Initializing {self.__class__.__name__}")

        self.X_THRESHOLD = x_threshold
        self.Y_THRESHOLD = y_threshold
        self.VELOCITY_COMPENSATION_X = velocity_compensation_x
        self.VELOCITY_COMPENSATION_Y = velocity_compensation_y

        self.screen_width, self.screen_height = MouseCtrl.screen_width, MouseCtrl.screen_height

    def check(self, landmark_data: LandmarkData) -> dict | None:
        if landmark_data.landmarks:
            left_ear = landmark_data.landmarks[93]
            right_ear = landmark_data.landmarks[323]
            head_top = landmark_data.landmarks[10]
            head_bottom = landmark_data.landmarks[152]

            nose = landmark_data.landmarks[4]

            head_width = abs(left_ear.x - right_ear.x)
            head_height = abs(head_top.y - head_bottom.y)

            distance_left = (nose.x - left_ear.x) / head_width
            distance_bottom = -1 * (nose.y - head_bottom.y) / head_height

            x_pos = (distance_left - 0.5) * 2
            y_pos = (distance_bottom - 0.5) * 2

            vec = np.array([x_pos, y_pos])

            if vec is None or (np.abs(vec) < [self.X_THRESHOLD, self.Y_THRESHOLD]).all():
                return

            log_vec = np.power(vec, 3) * self.screen_height
            rel_move = log_vec * [self.VELOCITY_COMPENSATION_X, -self.VELOCITY_COMPENSATION_Y]  # y inverted

            x, y = pyautogui.position()
            new_pos = np.array([x, y]) + rel_move

            # Clamp to screen dimensions
            new_pos = np.clip(new_pos, [0, 0], [self.screen_width - 1, self.screen_height - 1])

            return {"x": x_pos, "y": y_pos}
