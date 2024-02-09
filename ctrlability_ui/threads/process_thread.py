import logging
from PySide6.QtCore import QThread, Signal, Slot

log = logging.getLogger(__name__)


class ProcessThread(QThread):

    finished = Signal()
    update_required = Signal()  # for realtime changes in thread e.g. stream_handler (config dict)

    def __init__(self, model):
        super().__init__()

        self.model = model
        self.is_running = True
        self.update_required.connect(self.update_stream_handlers)
        self.stream_handlers = []

    def run(self):

        from ctrlability.core import bootstrapper

        self.stream_handlers = bootstrapper.boot()

        if log.isEnabledFor(logging.DEBUG):
            from ctrlability.util.tree_print import TreePrinter

            tree_printer = TreePrinter(self.stream_handlers, bootstrapper._mapping_engine)
            tree_printer.print_representation()

        while self.is_running:
            try:
                for stream in self.stream_handlers:
                    stream.process(None)
            except KeyboardInterrupt:
                log.info("KeyboardInterrupt: Exiting...")
                self.is_running = False
            self.msleep(10)  # FIX_MK Reduce CPU Usage / Improve Responsiveness

        self.finished.emit()

    def stop(self):
        self.is_running = False

    @Slot()
    def update_stream_handlers(self):
        print("/////////////////////////////Updating stream handlers...")
        self.is_running = False
        from ctrlability.core import bootstrapper

        self.stream_handlers = bootstrapper.boot()

        if log.isEnabledFor(logging.DEBUG):
            from ctrlability.util.tree_print import TreePrinter

            tree_printer = TreePrinter(self.stream_handlers, bootstrapper._mapping_engine)
            tree_printer.print_representation()
        self.is_running = True
        print("/////////////////////////////Updating stream handlers...DONE")
