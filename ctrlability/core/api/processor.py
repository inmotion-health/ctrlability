from abc import ABC, abstractmethod
from typing import List, Tuple
from uuid import UUID

from ctrlability.core.api.trigger import Trigger
from ctrlability.core.mapping_engine import MappingEngine


class Processor(ABC):
    def __init__(self, mapping_engine: MappingEngine):
        self._mapping_engine = mapping_engine
        self._triggers: List[Tuple[Trigger, UUID]] = []
        self._post_processors: List[Processor] = []

    def connect_trigger(self, trigger: Trigger, action_id: UUID):
        self._triggers.append((trigger, action_id))

    def connect_post_processor(self, post_processor):
        self._post_processors.append(post_processor)

    def process(self, data):
        data = self.compute(data)
        for post_processor in self._post_processors:
            post_processor.process(data)

        for trigger in self._triggers:
            d = trigger[0].check(data)
            if d:
                event_id = trigger[1]
                self._mapping_engine.notify(event_id, data=d)

    @abstractmethod
    def compute(self, data):
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}"
