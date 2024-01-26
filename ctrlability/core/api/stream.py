from abc import ABC, abstractmethod


class Stream(ABC):
    @abstractmethod
    def get_next(self):
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}"
