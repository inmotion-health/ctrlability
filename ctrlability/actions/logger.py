import logging

from ctrlability.core import Action, bootstrapper

log = logging.getLogger(__name__)


@bootstrapper.add()
class Logger(Action):
    """
    This class represents a logger action.

    Inputs:
        data: The data to be logged. This can be any type of data.

    It provides a method to execute the action and log the provided data.
    """

    def execute(self, data):
        log.debug(f"{data}")
