import inspect
from abc import ABC, abstractmethod
from typing import List, Tuple
from uuid import uuid4, UUID

from config_parser import ConfigParser


# TODO: add logging
# TODO: better naming
# TODO: think how ui can interact with the whole system
# TODO: thinking about async
# TODO: can we implement type detection of arguments while we parse the config
# TODO: separate into files/modules


class Trigger(ABC):
    @abstractmethod
    def check(self, data) -> dict | None:
        pass


class Action:
    @abstractmethod
    def execute(self, **kwargs):
        pass


class Stream(ABC):
    @abstractmethod
    def get_next(self):
        pass


class MappingEngine:
    def __init__(self):
        self._actions: dict[UUID, Action] = {}

    def register(self, action_id: UUID, action: Action):
        self._actions[action_id] = action

    def notify(self, action_id: UUID, **kwargs: object) -> object:
        print(kwargs)
        print("notify")
        print(self._actions[action_id])
        self._actions[action_id].execute(**kwargs)


class Processor(ABC):
    def __init__(self, mapping_engine: MappingEngine):
        self._mapping_engine = mapping_engine
        self._triggers: List[Tuple[Trigger, UUID]] = []
        self._post_processors: List[Processor] = []

    def connect_trigger(self, trigger: Trigger, action_id: UUID):
        self._triggers.append((trigger, action_id))

    def connect_post_processor(self, post_processor):
        self._post_processors.append(post_processor)

    def process(self, data):
        data = self.compute(data)
        for post_processor in self._post_processors:
            post_processor.process(data)

        for trigger in self._triggers:
            d = trigger[0].check(data)
            if d:
                event_id = trigger[1]
                self._mapping_engine.notify(event_id, data=d)

    @abstractmethod
    def compute(self, data):
        pass


class StreamHandler(Processor):
    def __init__(self, stream: Stream, mapping_engine: MappingEngine):
        super().__init__(mapping_engine)
        self._stream = stream
        self._mapping_engine = mapping_engine

    def _handle_stream(self):
        return self._stream.get_next()

    def compute(self, data):
        return self._handle_stream()

    def __repr__(self):
        return f"StreamHandler for {self._stream.__class__.__name__} -> " + super().__repr__()


# TODO: maybe use args for triggers - not kwargs
# TODO: return stream in better format. one more class? like one big handler. so much indirection >.<
# TODO: structure checking -> could be done in the config parser but alot of dup code for parsing/traversing
# TODO: split this parsing traversal into a separate class


class Bootstrapper:
    def __init__(self):
        self._config = ConfigParser().parse()
        self._mapping_engine = MappingEngine()
        self._classes = {}
        self.streams: list[StreamHandler] = []

    def bootstrap(self):
        print(self._classes)
        for stream in self._config.keys():
            args = self._config[stream].get("args", {})
            stream_instance = self.create_instance_from_name(stream, args)
            stream_handler = StreamHandler(stream_instance, self._mapping_engine)
            self.streams.append(stream_handler)

            for trigger in self._config[stream].get("triggers", []):
                self.parse_trigger(stream_handler, trigger)

            for processor in self._config[stream].get("processors"):
                self.parse_processor(processor, stream_handler)

        return self.streams

    def parse_processor(self, processor: dict, handler):
        # FIXME: unify arguments
        processor_name = self.block_name(processor)

        processor_instance = self.create_instance(processor, mapping_engine=self._mapping_engine)
        handler.connect_post_processor(processor_instance)

        post_processor = processor.get(processor_name).get("processors", [])
        print(processor_name)

        for trigger in processor.get(processor_name).get("triggers", []):
            self.parse_trigger(processor_instance, trigger)

        for pr in post_processor:
            print("PARSING POST PROCESSOR")
            self.parse_processor(pr, processor_instance)
            print("PARSED POST PROCESSOR")

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
                print(f"Argument {arg} is not valid for {cls.__name__} - ignoring")
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
