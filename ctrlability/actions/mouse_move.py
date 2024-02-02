import logging

from ctrlability.core import Action, bootstrapper
from ctrlability.helpers.mousectrl import MouseCtrl

log = logging.getLogger(__name__)


@bootstrapper.add()
class MoveMouse(Action):
    """
    A class representing an action to move the mouse to a specific position.
    """

    def execute(self, data):
        vec = [data["x"], data["y"]]
        MouseCtrl.move_mouse(vec)
