import inspect
import logging
from uuid import uuid4

import ctrlability.util.printing as printing
from ctrlability.engine.api import Action, Processor, Stream, Trigger
from ctrlability.engine.config_parser import ConfigParser
from ctrlability.engine.mapping_engine import MappingEngine
from ctrlability.engine.stream_handler import StreamHandler

log = logging.getLogger(__name__)


# TODO: maybe use args for triggers - not kwargs
# TODO: structure checking -> could be done in the config parser but alot of dup code for parsing/traversing
# TODO: can we implement type detection of arguments while we parse the config


class Bootstrapper:
    def __init__(self):
        self._config = ConfigParser().parse()
        self._mapping_engine = MappingEngine()
        self._classes = {}
        self.streams: list[StreamHandler] = []

    def boot(self):
        printing.debug_pprint(self._config)
        for stream_config in self._config:  # Iterate over each item in the list
            for stream, stream_info in stream_config.items():  # Now iterate over the dictionary
                args = stream_info.get("args", {})
                stream_instance = self.create_instance_from_name(stream, args)
                stream_handler = StreamHandler(stream_instance, self._mapping_engine)
                self.streams.append(stream_handler)

                for trigger in stream_info.get("triggers", []):
                    self.parse_trigger(stream_handler, trigger)

                for processor in stream_info.get("processors", []):  # Added default empty list
                    self.parse_processor(processor, stream_handler)

        return self.streams

    def parse_processor(self, processor: dict, handler):
        # FIXME: unify arguments
        processor_name = self.block_name(processor)

        processor_instance = self.create_instance(processor, mapping_engine=self._mapping_engine)
        handler.connect_post_processor(processor_instance)

        post_processor = processor.get(processor_name).get("processors", [])

        for trigger in processor.get(processor_name).get("triggers", []):
            self.parse_trigger(processor_instance, trigger)

        for pr in post_processor:
            log.debug("PARSING POST PROCESSOR")
            self.parse_processor(pr, processor_instance)
            log.debug("PARSED POST PROCESSOR")

    def parse_trigger(self, processor_instance, trigger):
        trigger_name = self.block_name(trigger)
        trigger_instance = self.create_instance(trigger)
        action = trigger.get(trigger_name).get("action", [])
        for action in action:
            # this is done because of the way how yaml is parsed
            # it allows to specify the action as a string or as a dict
            # you can just write - Printer or - Printer2:
            #                                      args: ...
            if isinstance(action, str):
                action_instance = self.find_class(action)()
            elif isinstance(action, dict):
                # todo: check keyword ags
                action_instance = self.create_instance(action)
            uu = uuid4()
            processor_instance.connect_trigger(trigger_instance, uu)
            self._mapping_engine.register(uu, action_instance)

    @staticmethod
    def block_name(block: dict) -> str:
        return list(block.keys())[0]

    def block_args(self, block: dict) -> dict:
        if not block.get(self.block_name(block)):
            return {}
        return block.get(self.block_name(block)).get("args", {})

    def create_instance(
        self, block: dict, mapping_engine: MappingEngine = None
    ) -> Action | Trigger | Processor | Stream:
        block_name = self.block_name(block)
        block_args = self.block_args(block)

        if mapping_engine:
            block_args["mapping_engine"] = mapping_engine
        return self.create_instance_from_name(block_name, block_args)

    @staticmethod
    def validate_args(cls, args: dict) -> dict:
        class_args = inspect.getfullargspec(cls.__init__)
        args_out = args.copy()
        for arg in args.keys():
            if arg not in class_args.args:
                log.error(f"Argument {arg} is not valid for {cls.__name__} - ignoring")
                args_out.pop(arg)
        return args_out

    def create_instance_from_name(self, name: str, args: dict) -> Action | Trigger | Processor | Stream:
        cls = self.find_class(name)
        args = self.validate_args(cls, args)
        return cls(**args)

    def find_class(self, class_name: str):
        return self._classes[class_name]

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
        flexible decorator to add classes to the mapping engine
        :param name: name which can be used to add the class - name that is used in the config file
        calling it like @add("MyClass") will add the class by the name "MyClass"
        calling it like @add()/@add will add the class by its classname
        """
        if name is None:
            return self.add_class_by_classname
        if isinstance(name, str):
            from functools import partial

            return partial(self.add_class_by_name, name)
        if inspect.isclass(name):
            return self.add_class_by_classname(name)
