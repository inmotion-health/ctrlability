import inspect
import logging
from uuid import uuid4

from ctrlability.engine.mapping_engine import MappingEngine

log = logging.getLogger(__name__)


class TreeParser:
    def __init__(self, classes, mapping_engine):
        self._classes = classes
        self._mapping_engine = mapping_engine

    def parse_processor(self, processor: dict, handler):
        processor_name = self.block_name(processor)

        processor_instance = self.create_instance(processor, mapping_engine=self._mapping_engine)
        handler.connect_post_processor(processor_instance)

        post_processor = processor.get(processor_name).get("processors", [])

        for trigger in processor.get(processor_name).get("triggers", []):
            self.parse_trigger(processor_instance, trigger)

        for pr in post_processor:
            log.debug("PARSING POST PROCESSOR...")
            self.parse_processor(pr, processor_instance)
            log.debug("PARSED POST PROCESSOR.")

    def parse_trigger(self, processor_instance, trigger):
        trigger_name = self.block_name(trigger)
        trigger_instance = self.create_instance(trigger)
        action = trigger.get(trigger_name).get("action", [])
        for action in action:
            if isinstance(action, str):
                action_instance = self.find_class(action)()
            elif isinstance(action, dict):
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

    def create_instance(self, block: dict, mapping_engine: MappingEngine = None):
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

    def create_instance_from_name(self, name: str, args: dict):
        cls = self.find_class(name)
        args = self.validate_args(cls, args)
        return cls(**args)

    def find_class(self, class_name: str):
        if class_name not in self._classes:
            raise RuntimeError(f"Class {class_name} not found. Did you forget to add it to the bootstrapper?")

        return self._classes[class_name]
