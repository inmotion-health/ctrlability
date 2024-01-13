import logging
from uuid import UUID

from ctrlability.engine.api.action import Action

log = logging.getLogger(__name__)


class MappingEngine:
    def __init__(self):
        self._actions: dict[UUID, Action] = {}

    def register(self, action_id: UUID, action: Action):
        self._actions[action_id] = action

    def notify(self, action_id: UUID, **kwargs: object) -> object:
        log.debug(f"notify: {action_id} with {kwargs}")
        self._actions[action_id].execute(**kwargs)
