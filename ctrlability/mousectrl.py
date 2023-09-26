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


class _state:
    is_tracking = False

    screen_width, screen_height = pyautogui.size()
    screen_center = (screen_width / 2, screen_height / 2)

    last_left_click_ms = 0
    left_click_count = 0

    is_mouse_frozen = False
    is_right_mouse_clicked = False


# MOUSE STATE

## TRACKING STATE


def set_tracking_mode(state):
    _state.is_tracking = state
    log.debug(f"Tracking mode set to {state}")


def is_tracking_enabled():
    return _state.is_tracking == True


## FREEZE STATE


def freeze_mouse_pos():
    if _state.is_mouse_frozen == True:
        return

    _state.is_mouse_frozen = True
    log.debug("Mouse position frozen")


def unfreeze_mouse_pos():
    if _state.is_mouse_frozen == False:
        return

    _state.is_mouse_frozen = False
    log.debug("Mouse position unfrozen")


def is_mouse_frozen():
    return _state.is_mouse_frozen


## LEFT CLICK STATE


def get_left_clicks():
    return _state.left_click_count


def release_left_click():
    _state.left_click_count = 0
    _state.last_left_click_ms = 0


def get_last_left_click_ms():
    return _state.last_left_click_ms


def increment_mouse_left_clicks():
    _state.left_click_count += 1


## RIGHT CLICK STATE


def get_right_click_state():
    return _state.is_right_mouse_clicked


def release_right_click():
    _state.is_right_mouse_clicked = False


# MOUSE MOVEMENT


def set_cursor_center():
    pyautogui.moveTo(_state.screen_center[0], _state.screen_center[1])
    log.debug("Cursor set to center of screen")


def move_mouse(vec):
    if vec is None:
        return

    # threshold for the distance to the center of the screen after which the mouse will move
    X_THRESHOLD = 0.05
    Y_THRESHOLD = 0.03

    mouse_can_move = abs(vec[0]) > X_THRESHOLD or abs(vec[1]) > Y_THRESHOLD

    if mouse_can_move:
        # scale the vector to a cubic function for smoother movement
        log_vec = np.power(np.array(vec), 3)

        log_vec *= _state.screen_height

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
        if 0 <= new_x < _state.screen_width and 0 <= new_y < _state.screen_height:
            pyautogui.moveRel(v_x, v_y)
        else:
            # Adjust new_x and new_y if they would be off screen
            if new_x < 0:
                new_x = 0
            elif new_x >= _state.screen_width:
                new_x = _state.screen_width - 1

            if new_y < 0:
                new_y = 0
            elif new_y >= _state.screen_height:
                new_y = _state.screen_height - 1

            # Move to the adjusted position with a smooth transition
            pyautogui.moveTo(new_x, new_y)


# MOUSE CLICKS


def left_click():
    pyautogui.click()
    _state.last_left_click_ms = time.time() * 1000
    _state.left_click_count += 1
    log.debug("Left click")


def double_click():
    if platform.system() == "Darwin":
        macmouse.double_click()
    else:
        pyautogui.doubleClick()

    _state.last_left_click_ms = time.time() * 1000
    log.debug("Double click")


def right_click():
    pyautogui.rightClick()
    _state.is_right_mouse_clicked = True
    log.debug("Right click")
