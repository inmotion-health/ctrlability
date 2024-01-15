from ctrlability.core.api.processor import Processor
from ctrlability.core.api.stream import Stream
from ctrlability.core.mapping_engine import MappingEngine


class StreamHandler(Processor):
    def __init__(self, stream: Stream, mapping_engine: MappingEngine):
        super().__init__(mapping_engine)
        self._stream = stream
        self._mapping_engine = mapping_engine

    def _handle_stream(self):
        return self._stream.get_next()

    def compute(self, data):
        return self._handle_stream()
