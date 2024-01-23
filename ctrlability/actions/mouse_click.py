from ctrlability.core import Action, bootstrapper
from ctrlability.helpers.mousectrl import MouseCtrl

# TODO: implement all fine grained freezing, unfreezing and checks for which click can be done when


@bootstrapper.add()
class MouseClick(Action):
    _LEFT = "left"
    _RIGHT = "right"
    _DOUBLE = "double"

    def __init__(self, key_name):
        self.key = key_name

        # check if key_name is valid
        if self.key not in [self._LEFT, self._RIGHT, self._DOUBLE]:
            raise ValueError(f"Invalid key: {self.key}")

    def execute(self, data):
        MouseCtrl.freeze_mouse_pos()

        if self.key == self._LEFT:
            MouseCtrl.left_click()
        elif self.key == self._RIGHT:
            MouseCtrl.right_click()
        elif self.key == self._DOUBLE:
            MouseCtrl.double_click()

        MouseCtrl.unfreeze_mouse_pos()

    def __repr__(self):
        return f"MouseClick(key: {self.key})"
