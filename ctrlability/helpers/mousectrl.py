import logging
import platform
from abc import ABC, abstractmethod

import numpy as np
import pyautogui

if platform.system() == "Darwin":
    import macmouse

log = logging.getLogger(__name__)

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.0
pyautogui.DARWIN_CATCH_UP_TIME = 0.00


class MouseActions(ABC):
    @abstractmethod
    def double_click(self):
        pass


class MacMouseActions(MouseActions):
    def double_click(self):
        macmouse.double_click()


class DefaultMouseActions(MouseActions):
    def double_click(self):
        pyautogui.doubleClick()


class _MouseCtrl:
    def __init__(self, mouse_actions: MouseActions):
        self.mouse_actions = mouse_actions

        self.is_tracking_enabled = False

        self.screen_width, self.screen_height = pyautogui.size()
        self.screen_center = (self.screen_width / 2, self.screen_height / 2)

        self.last_left_click_ms = 0
        self.left_click_count = 0

        self.is_mouse_frozen = False
        self.is_right_mouse_clicked = False

        self.scroll_mode = False

        # default values
        self.X_THRESHOLD = None
        self.Y_THRESHOLD = None
        self.VELOCITY_COMPENSATION_X = None
        self.VELOCITY_COMPENSATION_Y = None
        self.setup_counter = 0

    def set_settings(self, settings):
        if self.setup_counter > 0:
            raise RuntimeError(
                "MouseCtrl settings can only be set once. You migh have multiple cursor control triggers."
            )

        self.X_THRESHOLD = settings["x_threshold"]
        self.Y_THRESHOLD = settings["y_threshold"]
        self.VELOCITY_COMPENSATION_X = settings["velocity_compensation_x"]
        self.VELOCITY_COMPENSATION_Y = settings["velocity_compensation_y"]

        self.setup_counter += 1

    # TRACKING STATE
    def set_tracking_mode(self, state: bool):
        self.is_tracking_enabled = state
        log.debug(f"Tracking mode set to {state}")

    # FREEZE STATE
    def freeze_mouse_pos(self):
        if self.is_mouse_frozen:
            return

        self.is_mouse_frozen = True
        log.debug("Mouse position frozen")

    def unfreeze_mouse_pos(self):
        if not self.is_mouse_frozen:
            return

        self.is_mouse_frozen = False
        log.debug("Mouse position unfrozen")

    # MOUSE MOVEMENT
    def set_cursor_center(self):
        pyautogui.moveTo(self.screen_center[0], self.screen_center[1])
        log.debug("Cursor set to center of screen")

    def move_mouse(self, vec: np.array) -> None:
        if self.is_mouse_frozen:
            return

        if vec is None or (np.abs(vec) < [self.X_THRESHOLD, self.Y_THRESHOLD]).all():
            return

        log_vec = np.power(vec, 3) * self.screen_height
        rel_move = log_vec * [self.VELOCITY_COMPENSATION_X, -self.VELOCITY_COMPENSATION_Y]  # y inverted

        x, y = pyautogui.position()
        new_pos = np.array([x, y]) + rel_move

        # Clamp to screen dimensions
        new_pos = np.clip(new_pos, [0, 0], [self.screen_width - 1, self.screen_height - 1])

        if self.scroll_mode:
            pyautogui.scroll(50)
        else:
            pyautogui.moveTo(*new_pos)

    # MOUSE CLICKS
    def left_click(self):
        pyautogui.click()
        log.debug("Left click")

    def double_click(self):
        self.mouse_actions.double_click()
        log.debug("Double click")

    def right_click(self):
        pyautogui.rightClick()
        log.debug("Right click")

    def left_down(self):
        pyautogui.mouseDown()
        log.debug("Left down")

    def left_up(self):
        pyautogui.mouseUp()
        log.debug("Left up")


# Singleton instance
if platform.system() == "Darwin":
    mouse_actions = MacMouseActions()
else:
    mouse_actions = DefaultMouseActions()

MouseCtrl = _MouseCtrl(mouse_actions)
