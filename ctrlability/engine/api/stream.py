from abc import ABC, abstractmethod


class Stream(ABC):
    @abstractmethod
    def get_next(self):
        pass
