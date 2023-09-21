import pyautogui
import platform
import numpy as np

if platform.system() == "Darwin":
    import macmouse


class MouseCtrl:
    AUTO_MODE = False

    def __init__(self):
        self._screen_width, self._screen_height = pyautogui.size()
        self._screen_center = (self._screen_width / 2, self._screen_height / 2)
        self.mouse_left_clicks = 0
        self.frozen_mouse_pos = False
        self.right_mouse_clicked = False
        self.last_left_click_ms = 0

    def set_center(self):
        pyautogui.moveTo(self._screen_center[0], self._screen_center[1])

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

            log_vec *= self._screen_height

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
            if 0 <= new_x < self._screen_width and 0 <= new_y < self._screen_height:
                pyautogui.moveRel(v_x, v_y)
            else:
                # Adjust new_x and new_y if they would be off screen
                if new_x < 0:
                    new_x = 0
                elif new_x >= self._screen_width:
                    new_x = self._screen_width - 1

                if new_y < 0:
                    new_y = 0
                elif new_y >= self._screen_height:
                    new_y = self._screen_height - 1

                # Move to the adjusted position with a smooth transition
                pyautogui.moveTo(new_x, new_y)

    def left_click(self):
        pyautogui.click()

    def double_click(self):
        if platform.system() == "Darwin":
            macmouse.double_click()
        else:
            pyautogui.doubleClick()

    def right_click(self):
        pyautogui.rightClick()
        self.right_mouse_clicked = True
