import logging

from ctrlability.core import Action, bootstrapper

log = logging.getLogger(__name__)


@bootstrapper.add()
class Logger(Action):
    def execute(self, data):
        log.debug(f"{data}")
