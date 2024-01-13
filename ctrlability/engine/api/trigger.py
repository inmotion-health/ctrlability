from abc import ABC, abstractmethod


class Trigger(ABC):
    @abstractmethod
    def check(self, data) -> dict | None:
        pass
