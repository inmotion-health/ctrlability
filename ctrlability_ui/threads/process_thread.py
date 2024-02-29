import logging
from PySide6.QtCore import QThread, Signal, Slot, QMutex, QWaitCondition
from ctrlability.processors import VideoFrameGrabber

log = logging.getLogger(__name__)


# MK_Fix: improve the Process Thread
class ProcessThread(QThread):

    finished = Signal()
    update_required = Signal()
    new_frame = Signal(object)
    expressions = Signal(float, float, float, float)

    def __init__(self, model):
        super().__init__()
        self.is_running = True
        self.is_paused = True
        self.model = model
        self.update_required.connect(self.update_stream_handlers)
        self.stream_handlers = []

        self.mutex = QMutex()
        self.pause_condition = QWaitCondition()

    def run(self):

        from ctrlability.core import bootstrapper

        self.stream_handlers = bootstrapper.boot()
        self.connectVideoFrameGrabber(bootstrapper)

        if log.isEnabledFor(logging.DEBUG):
            from ctrlability.util.tree_print import TreePrinter

            tree_printer = TreePrinter(self.stream_handlers, bootstrapper._mapping_engine)
            tree_printer.print_representation()

        while self.is_running:
            self.mutex.lock()
            try:
                if self.is_paused:
                    self.pause_condition.wait(self.mutex)
                    self.msleep(10)
                    continue

                for stream in self.stream_handlers:
                    stream.process(None)

                expression_score1 = (
                    self.stream_handlers[0]._post_processors[0]._post_processors[0]._triggers[0][0].score
                )
                expression_score2 = (
                    self.stream_handlers[0]._post_processors[0]._post_processors[0]._triggers[1][0].score
                )
                expression_score3 = (
                    self.stream_handlers[0]._post_processors[0]._post_processors[0]._triggers[2][0].score
                )
                expression_score4 = (
                    self.stream_handlers[0]._post_processors[0]._post_processors[0]._triggers[3][0].score
                )
                self.expressions.emit(expression_score1, expression_score2, expression_score3, expression_score4)

            finally:
                self.mutex.unlock()
            self.msleep(10)  # FIX_MK Reduce CPU Usage / Improve Responsiveness

    def stop(self):
        log.debug("Stopping process thread...")
        self.resume()
        self.is_running = False
        self.wait()  # Optionally wait for the thread to finish

    def pause(self):
        self.mutex.lock()
        self.is_paused = True
        self.mutex.unlock()

    def resume(self):
        self.mutex.lock()
        self.is_paused = False
        self.mutex.unlock()
        self.pause_condition.wakeAll()  # Wake the thread if it's waiting

    def connectVideoFrameGrabber(self, bootstrapper):
        _mapping_engine = bootstrapper._mapping_engine
        video_frame_grabber = VideoFrameGrabber(_mapping_engine, self.new_frame)
        self.stream_handlers[0].connect_post_processor(video_frame_grabber)

    @Slot()
    def update_stream_handlers(self):
        self.mutex.lock()
        try:
            from ctrlability.core import bootstrapper

            bootstrapper.reset()
            self.stream_handlers = bootstrapper.boot()
            self.connectVideoFrameGrabber(bootstrapper)

            if log.isEnabledFor(logging.DEBUG):
                from ctrlability.util.tree_print import TreePrinter

                tree_printer = TreePrinter(self.stream_handlers, bootstrapper._mapping_engine)
                tree_printer.print_representation()
        finally:
            self.mutex.unlock()
        log.debug("Stream handlers updated.")
