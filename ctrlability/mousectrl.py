import logging as log
import platform
import time
from abc import ABC, abstractmethod

import numpy as np
import pyautogui

if platform.system() == "Darwin":
    import macmouse

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.0
pyautogui.DARWIN_CATCH_UP_TIME = 0.00

X_THRESHOLD = 0.05
Y_THRESHOLD = 0.03
VELOCITY_COMPENSATION_X = 0.15
VELOCITY_COMPENSATION_Y = 3.5
SIGMOID_FACTOR = 6


# FIXME: not behaving as expected
def sigmoid_smoothing(vec: np.array) -> np.array:
    vec = np.array(vec)  # FIXME: not sure why we have to do this at this point

    def sigmoid(x):
        return 1 / (1 + np.exp(-SIGMOID_FACTOR * x))

    def adjusted_sigmoid(x):
        return (sigmoid(2 * x - 1) - sigmoid(-SIGMOID_FACTOR)) / (sigmoid(SIGMOID_FACTOR) - sigmoid(-SIGMOID_FACTOR))

    for x in vec:
        if x > 0:
            x = adjusted_sigmoid(x)
        else:
            x = -adjusted_sigmoid(-x)

    return vec


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

    # MOUSE STATE
    ## TRACKING STATE
    def set_tracking_mode(self, state: bool):
        self.is_tracking_enabled = state
        log.debug(f"Tracking mode set to {state}")

    ## FREEZE STATE
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

    def release_left_click(self):
        self.left_click_count = 0
        self.last_left_click_ms = 0

    def release_right_click(self):
        self.is_right_mouse_clicked = False

    # MOUSE MOVEMENT
    def set_cursor_center(self):
        pyautogui.moveTo(self.screen_center[0], self.screen_center[1])
        log.debug("Cursor set to center of screen")

    def move_mouse(self, vec: np.array) -> None:
        if vec is None or (np.abs(vec) < [X_THRESHOLD, Y_THRESHOLD]).all():
            return

        # log_vec = sigmoid_smoothing(vec) * self.screen_height
        log_vec = np.power(vec, 3) * self.screen_height
        rel_move = log_vec * [VELOCITY_COMPENSATION_X, -VELOCITY_COMPENSATION_Y]  # y inverted

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
        self.last_left_click_ms = time.time() * 1000
        self.left_click_count += 1
        log.debug("Left click")

    def double_click(self):
        self.mouse_actions.double_click()

        self.last_left_click_ms = time.time() * 1000
        log.debug("Double click")

    def right_click(self):
        pyautogui.rightClick()
        self.is_right_mouse_clicked = True
        log.debug("Right click")


# Singleton instance
if platform.system() == "Darwin":
    mouse_actions = MacMouseActions()
else:
    mouse_actions = DefaultMouseActions()

MouseCtrl = _MouseCtrl(mouse_actions)
