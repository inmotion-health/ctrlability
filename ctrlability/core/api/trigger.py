from abc import ABC, abstractmethod


class Trigger(ABC):
    @abstractmethod
    def check(self, data) -> dict | None:
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}"
