from ctrlability.core import Action, bootstrapper
from ctrlability.helpers.mousectrl import MouseCtrl


@bootstrapper.add()
class MouseClick(Action):
    _LEFT = "left"
    _RIGHT = "right"
    _DOUBLE = "double"
    _LEFT_DOWN = "left_down"
    _LEFT_UP = "left_up"

    def __init__(self, key_name):
        self.key = key_name

        # check if key_name is valid
        if self.key not in [self._LEFT, self._RIGHT, self._DOUBLE, self._LEFT_DOWN, self._LEFT_UP]:
            raise ValueError(f"Invalid key: {self.key}")

    def execute(self, data):
        MouseCtrl.freeze_mouse_pos()

        if self.key == self._LEFT:
            MouseCtrl.left_click()
        elif self.key == self._RIGHT:
            MouseCtrl.right_click()
        elif self.key == self._DOUBLE:
            MouseCtrl.double_click()
        elif self.key == self._LEFT_DOWN:
            MouseCtrl.left_down()
        elif self.key == self._LEFT_UP:
            MouseCtrl.left_up()

        MouseCtrl.unfreeze_mouse_pos()

    def __repr__(self):
        return f"MouseClick(key: {self.key})"
