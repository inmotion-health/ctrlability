import logging

from ctrlability.core import Action, bootstrapper
from ctrlability.helpers.mousectrl import MouseCtrl

log = logging.getLogger(__name__)


@bootstrapper.add()
class MoveMouse(Action):
    def execute(self, data):
        vec = [data["x"], data["y"]]
        MouseCtrl.move_mouse(vec)
