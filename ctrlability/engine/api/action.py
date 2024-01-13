from abc import abstractmethod


class Action:
    @abstractmethod
    def execute(self, **kwargs):
        pass
