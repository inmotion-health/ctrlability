import ctrlability.util.printing as printing


class TreePrinter:
    def __init__(self, stream_handlers, mapping_engine):
        self.streams = stream_handlers
        self.mapping_engine = mapping_engine

        self.VERTICAL = "│"
        self.TEE = "├"
        self.CORNER = "└"
        self.HORIZONTAL = "─"

    def print_representation(self):
        printing.print_line()
        print("Tree representation of the mapping engine:")
        for index, stream_handler in enumerate(self.streams):
            last_stream = index == len(self.streams) - 1
            self._print_stream(stream_handler, "", last_stream)

        printing.print_line()

    def _print_stream(self, stream_handler, prefix="", last_stream=False):
        stream = stream_handler._stream
        print(f"{prefix}{self.CORNER if last_stream else self.TEE}{self.HORIZONTAL} {stream}")

        if stream_handler._post_processors:
            new_prefix = prefix + ("  " if last_stream else self.VERTICAL + " ")
            for index, post_processor in enumerate(stream_handler._post_processors):
                last_processor = index == len(stream_handler._post_processors) - 1
                self._print_processor(post_processor, new_prefix, last_processor)

    def _print_trigger(self, trigger, uuid, prefix, last_trigger):
        print(f"{prefix}{self.TEE}{self.HORIZONTAL} {trigger}")
        action = self.mapping_engine._actions[uuid]
        print(f"{prefix}{' ' * 5}-> {action}")

    def _print_processor(self, processor, prefix, last_processor):
        print(f"{prefix}{self.CORNER if last_processor else self.TEE}{self.HORIZONTAL} {processor}")

        last_trigger_index = len(processor._triggers) - 1
        for index, (trigger, uuid) in enumerate(processor._triggers):
            self._print_trigger(
                trigger, uuid, prefix + ("  " if last_processor else self.VERTICAL + " "), index == last_trigger_index
            )

        for index, post_processor in enumerate(processor._post_processors):
            last_post_processor = index == len(processor._post_processors) - 1
            self._print_processor(
                post_processor, prefix + ("  " if last_processor else self.VERTICAL + " "), last_post_processor
            )
