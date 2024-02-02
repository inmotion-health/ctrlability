import logging

import numpy as np

from ctrlability.core import Trigger, bootstrapper
from ctrlability.core.data_types import NormalVectorData
from ctrlability.helpers.mousectrl import MouseCtrl
from ctrlability.math.geometry import distance_between_points
from ctrlability.math.one_euro_filter import OneEuroFilter

log = logging.getLogger(__name__)


@bootstrapper.add()
class AbsoluteCursorControl(Trigger):
    """
    A trigger that moves the cursor to the position of the nose tip in the 2D space. We project a vector from a specific
    landmark first using the normal vector and then translate the nose tip to the screen space.

    !! This trigger only works with facial landmarks !!

    Inputs:
        NormalVectorData: The normal vector of the landmark.

    Returns:
        dict: The x and y coordinates of the landmark tip in the screen space.

    Args:
        rect_width: The width of the rectangle around the nose tip (default: 0.8).
        head_width: The width of the head (default: 0.3).
    """

    def __init__(self, rect_width=0.8, head_width=0.3):
        self.rect_width = rect_width
        self.head_width = head_width

        self.screen_width, self.screen_height = MouseCtrl.screen_width, MouseCtrl.screen_height

        self.oef_1 = OneEuroFilter(t0=0, x0=0, min_cutoff=0.01, beta=0.005)
        self.oef_2 = OneEuroFilter(t0=0, x0=0, min_cutoff=0.001, beta=0.001)

        self.counter = 0

    def check(self, normal_vector_data: NormalVectorData) -> dict | None:
        if normal_vector_data is None:
            return None

        # let's scale the width of the rectangle to the width of the head, so we reduce the impact of the distance to
        # the camera
        head_left = normal_vector_data.landmarks[234]
        head_right = normal_vector_data.landmarks[454]

        head_width = distance_between_points(head_left, head_right)
        rect_width = self.rect_width * head_width / self.head_width

        # draw rectangle around the base of the normal vector
        nose = normal_vector_data.base

        # since we're working with normalized coordinates, we need don't need to scale to the aspect ratio here and just
        # use assume square
        rect_height = rect_width

        rect_x = nose[0] - rect_width / 2
        rect_y = nose[1] - rect_height / 2

        self.counter += 1
        nose_tip_2D_extended = self.oef_1(self.counter, normal_vector_data.tip)

        # translate nose tip to the rectangle
        translated_nose_tip = nose_tip_2D_extended - [rect_x, rect_y]
        translated_nose_tip = translated_nose_tip / [rect_width, rect_height]

        # scale nose tip to screen size and clip to screen size
        translated_nose_tip = translated_nose_tip * [self.screen_width, self.screen_height]
        translated_nose_tip = np.clip(translated_nose_tip, [0, 0], [self.screen_width, self.screen_height])

        translated_nose_tip = self.oef_2(self.counter, translated_nose_tip)

        return {"x": translated_nose_tip[0], "y": translated_nose_tip[1]}
