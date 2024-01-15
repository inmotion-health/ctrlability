import inspect
import logging

from ctrlability.engine.config_parser import ConfigParser
from ctrlability.engine.mapping_engine import MappingEngine
from ctrlability.engine.stream_handler import StreamHandler
from ctrlability.engine.tree_parser import TreeParser
from ctrlability.util import printing

log = logging.getLogger(__name__)


# TODO: maybe use args for triggers - not kwargs
# TODO: structure checking -> could be done in the config parser but alot of dup code for parsing/traversing
# TODO: can we implement type detection of arguments while we parse the config


class Bootstrapper:
    def __init__(self):
        self._config = ConfigParser().parse()
        self._mapping_engine = MappingEngine()
        self._classes = {}
        self.streams = []
        self._tree_parser = TreeParser(self._classes, self._mapping_engine)

    def boot(self):
        printing.debug_pprint(self._config)
        for stream, stream_info in self._config.items():  # Iterate over the dictionary
            args = stream_info.get("args", {})
            stream_instance = self._tree_parser.create_instance_from_name(stream, args)
            stream_handler = StreamHandler(stream_instance, self._mapping_engine)
            self.streams.append(stream_handler)

            # Processors are a list of dictionaries
            for processor_dict in stream_info.get("processors", []):
                for processor_name, processor_info in processor_dict.items():
                    processor = {processor_name: processor_info}
                    self._tree_parser.parse_processor(processor, stream_handler)

        return self.streams

    def add_class(self, name, class_):
        self._classes[name] = class_

    def add_class_by_name(self, name, class_):
        self._classes[name] = class_
        return class_

    def add_class_by_classname(self, class_):
        self._classes[class_.__name__] = class_
        return class_

    def add(self, name=None):
        """
        Flexible decorator to add classes to the mapping engine.
        :param name: Name which can be used to add the class - the name that is used in the config file.
                    Calling it like @add("MyClass") will add the class by the name "MyClass".
                    Calling it like @add()/@add will add the class by its classname.
        """
        if name is None:
            return self.add_class_by_classname
        if isinstance(name, str):
            from functools import partial

            return partial(self.add_class_by_name, name)
        if inspect.isclass(name):
            return self.add_class_by_classname(name)
