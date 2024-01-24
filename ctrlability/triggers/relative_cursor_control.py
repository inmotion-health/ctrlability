import logging

from ctrlability.core import Trigger, bootstrapper
from ctrlability.helpers.mousectrl import MouseCtrl

log = logging.getLogger(__name__)


@bootstrapper.add()
class RelativeCursorControl(Trigger):
    def __init__(self, x_threshold=0.05, y_threshold=0.03, velocity_compensation_x=0.15, velocity_compensation_y=3.5):
        log.debug(f"Initializing {self.__class__.__name__}")

        settings = {
            "x_threshold": x_threshold,
            "y_threshold": y_threshold,
            "velocity_compensation_x": velocity_compensation_x,
            "velocity_compensation_y": velocity_compensation_y,
        }

        MouseCtrl.set_settings(settings)

        log.debug(f"RelativeCursorControl settings: {settings}")

    def check(self, data) -> dict | None:
        if data:
            left_ear = data[93]
            right_ear = data[323]
            head_top = data[10]
            head_bottom = data[152]

            nose = data[4]

            head_width = abs(left_ear.x - right_ear.x)
            head_height = abs(head_top.y - head_bottom.y)

            distance_left = (nose.x - left_ear.x) / head_width
            distance_bottom = -1 * (nose.y - head_bottom.y) / head_height

            x_pos = (distance_left - 0.5) * 2
            y_pos = (distance_bottom - 0.5) * 2

            return {"x": x_pos, "y": y_pos}
