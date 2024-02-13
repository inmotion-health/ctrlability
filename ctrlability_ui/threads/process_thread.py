import logging
from PySide6.QtCore import QThread, Signal, Slot, QMutex, QMutexLocker

log = logging.getLogger(__name__)


class ProcessThread(QThread):

    finished = Signal()
    update_required = Signal()

    def __init__(self, model):
        super().__init__()
        self.is_running = True
        self.model = model
        self.update_required.connect(self.update_stream_handlers)
        self.stream_handlers = []
        self.mutex = QMutex()

    def run(self):

        from ctrlability.core import bootstrapper

        self.stream_handlers = bootstrapper.boot()

        if log.isEnabledFor(logging.DEBUG):
            from ctrlability.util.tree_print import TreePrinter

            tree_printer = TreePrinter(self.stream_handlers, bootstrapper._mapping_engine)
            tree_printer.print_representation()

        while self.is_running:
            self.mutex.lock()
            try:
                for stream in self.stream_handlers:
                    stream.process(None)
            finally:
                self.mutex.unlock()
            self.msleep(10)  # FIX_MK Reduce CPU Usage / Improve Responsiveness

    def stop(self):
        log.debug("Stopping process thread...")
        self.is_running = False
        self.wait()  # Optionally wait for the thread to finish

    @Slot()
    def update_stream_handlers(self):
        self.mutex.lock()
        try:
            from ctrlability.core import bootstrapper

            bootstrapper.reset()
            self.stream_handlers = bootstrapper.boot()

            if log.isEnabledFor(logging.DEBUG):
                from ctrlability.util.tree_print import TreePrinter

                tree_printer = TreePrinter(self.stream_handlers, bootstrapper._mapping_engine)
                tree_printer.print_representation()
        finally:
            self.mutex.unlock()
        log.debug("Stream handlers updated.")
