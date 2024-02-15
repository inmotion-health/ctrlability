from ctrlability.core import Processor, MappingEngine, bootstrapper
from ctrlability.core.data_types import FrameData


@bootstrapper.add()
class VideoFrameGrabber(Processor):

    def __init__(self, mapping_engine: MappingEngine, signal):
        super().__init__(mapping_engine)
        self.signal = signal

    def compute(self, data: FrameData):
        self.signal.emit(data)
