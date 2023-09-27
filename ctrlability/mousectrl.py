import time
import pyautogui
import platform
import numpy as np

import logging as log

if platform.system() == "Darwin":
    import macmouse

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.0
pyautogui.DARWIN_CATCH_UP_TIME = 0.00


class _MouseCtrl:
    def __init__(self):
        self.is_tracking_enabled = False

        self.screen_width, self.screen_height = pyautogui.size()
        self.screen_center = (self.screen_width / 2, self.screen_height / 2)

        self.last_left_click_ms = 0
        self.left_click_count = 0

        self.is_mouse_frozen = False
        self.is_right_mouse_clicked = False

    # MOUSE STATE
    ## TRACKING STATE
    def set_tracking_mode(self, state):
        self.is_tracking_enabled = state
        log.debug(f"Tracking mode set to {state}")

    ## FREEZE STATE
    def freeze_mouse_pos(self):
        if self.is_mouse_frozen == True:
            return

        self.is_mouse_frozen = True
        log.debug("Mouse position frozen")

    def unfreeze_mouse_pos(self):
        if self.is_mouse_frozen == False:
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

    def move_mouse(self, vec):
        if vec is None:
            return

        # threshold for the distance to the center of the screen after which the mouse will move
        X_THRESHOLD = 0.05
        Y_THRESHOLD = 0.03

        mouse_can_move = abs(vec[0]) > X_THRESHOLD or abs(vec[1]) > Y_THRESHOLD

        if mouse_can_move:
            # scale the vector to a cubic function for smoother movement
            log_vec = np.power(np.array(vec), 3)

            log_vec *= self.screen_height

            # we need to compensate for a higher velocity in the y direction
            VELOCITY_COMPENSATION_X = 0.5
            VELOCITY_COMPENSATION_Y = 5

            v_x = log_vec[0] * VELOCITY_COMPENSATION_X
            v_y = -1 * log_vec[1] * VELOCITY_COMPENSATION_Y  # y is inverted

            x, y = pyautogui.position()
            # Calculate the new position after the relative move
            new_x = x + v_x
            new_y = y + v_y

            # check if new position is on screen
            if 0 <= new_x < self.screen_width and 0 <= new_y < self.screen_height:
                pyautogui.moveRel(v_x, v_y)
            else:
                # Adjust new_x and new_y if they would be off screen
                if new_x < 0:
                    new_x = 0
                elif new_x >= self.screen_width:
                    new_x = self.screen_width - 1

                if new_y < 0:
                    new_y = 0
                elif new_y >= self.screen_height:
                    new_y = self.screen_height - 1

                # Move to the adjusted position with a smooth transition
                pyautogui.moveTo(new_x, new_y)

    # MOUSE CLICKS
    def left_click(self):
        pyautogui.click()
        self.last_left_click_ms = time.time() * 1000
        self.left_click_count += 1
        log.debug("Left click")

    def double_click(self):
        if platform.system() == "Darwin":
            macmouse.double_click()
        else:
            pyautogui.doubleClick()

        self.last_left_click_ms = time.time() * 1000
        log.debug("Double click")

    def right_click(self):
        pyautogui.rightClick()
        self.is_right_mouse_clicked = True
        log.debug("Right click")


# Singleton instance
MouseCtrl = _MouseCtrl()
