from abc import abstractmethod


class Action:
    @abstractmethod
    def execute(self, **kwargs):
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}"
