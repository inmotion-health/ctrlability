from ctrlability.core import Trigger, bootstrapper


@bootstrapper.add()
class Throughput(Trigger):
    def check(self, data) -> dict | None:
        return data
