from ctrlability.core import Processor, MappingEngine, bootstrapper


@bootstrapper.add()
class SignalDivider(Processor):
    """
    SignalDivider class

    This class represents a signal divider that divides input data and returns the specified index value. This class can,
    for example, be used to split the output of the Holistic Landmark Processor into the different body parts.
    """

    def __init__(self, mapping_engine: MappingEngine, index: int = 0):
        super().__init__(mapping_engine)

        self.index = index

    def compute(self, data):
        if data is None:
            return

        return data[self.index]
