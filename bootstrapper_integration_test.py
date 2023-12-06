from mapping_engine import Stream, Trigger, Action, Processor, Bootstrapper


class NumberStream(Stream):
    def __init__(self):
        self._number = 0

    def get_next(self):
        print("get_next stream")
        return 10


class Multiplier(Processor):
    def compute(self, data):
        print("mutliplier")
        return data * self._number

    def __init__(self, factor=2, mapping_engine=None):
        super().__init__(mapping_engine)
        self._number = factor


class Printer(Action):

    def __init__(self):
        pass

    def execute(self, **kwargs):
        print("FUCKING TRIGGERED")


class BiggerThan(Trigger):
    def __init__(self, number):
        self._number = number

    def check(self, data):
        print("bigger")
        return 3


b = Bootstrapper()


@b.add("Truer")
class Truer(Trigger):

    def check(self, data):
        print("SOWIESO")
        return True


@b.add("Printer2")
class Printer2(Action):

    def __init__(self, message=3):
        print("INIT")
        print(message)
        self.message = message

    def execute(self, **kwargs):
        print(self.message)
        print("YAAA")
        return True


b.add_class('NumberStream', NumberStream)
b.add_class('Multiplier', Multiplier)
b.add_class('Printer', Printer)
b.add_class('BiggerThan', BiggerThan)
b.add_class("Multiplierrr", Multiplier)

if __name__ == '__main__':
    streams = b.bootstrap()
    print(streams)
    for stream in streams:
        stream.process(None)
