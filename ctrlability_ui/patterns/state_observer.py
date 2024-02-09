class CtrlAbilityStateObserver:
    _observers = []

    @classmethod
    def register(cls, observer):
        cls._observers.append(observer)

    @classmethod
    def notify(cls, state):
        for observer in cls._observers:
            observer.update(state)
