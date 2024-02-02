from ctrlability.core import Trigger, bootstrapper


@bootstrapper.add()
class Throughput(Trigger):
    """
    A trigger that passes through the data without any modifications and hence always triggers. This is useful for
    testing and debugging purposes.
    """

    def check(self, data) -> dict | None:
        return data
