import logging
from ctrlability_ui.patterns.state_observer import CtrlAbilityStateObserver
from ctrlability_ui.threads.process_thread import ProcessThread

from PySide6.QtCore import QObject, Qt, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QMessageBox,
    QFileDialog,
)

log = logging.getLogger(__name__)


# Controller
class CtrlAbilityController(QObject):
    def __init__(self, model, view):
        super().__init__()
        self.model = model
        self.view = view

        # INITIALIZE VIDEO MANAGER
        # self.video_manager = VideoManager()
        # print(self.video_manager.list_available_cameras())
        # self.video_manager.set_preferred_height(480)

        # self.webcam_source = self.video_manager.get_video_source(0)
        # self.width = self.webcam_source.get_width()
        # self.height = self.webcam_source.get_height()
        # self.qImage = QImage(self.width, self.height, QImage.Format_RGB888)

        self.view.sideMenu.itemClicked.connect(self.on_side_menu_item_clicked)

        ## Status Menu actions
        self.view.aboutAction.triggered.connect(self.show_about_dialog)
        self.view.loadAction.triggered.connect(self.load_file)
        self.view.saveAction.triggered.connect(self.save_file)
        self.view.helpAction.triggered.connect(self.show_help_dialog)

        ## HeadFaceView actions
        self.view.mainView.headFaceView.cam_combo_box.currentIndexChanged.connect(self.head_face_view_on_cam_changed)
        self.view.mainView.headFaceView.face_expression_comp1.simulate_confidence_change(60)
        self.view.mainView.headFaceView.face_expression_comp2.simulate_confidence_change(40)

        self.model.load_state()
        # self.view.update(self.model.state)
        # self.update(self.model.state)

        # select HeadFaceView in the side menu as the default view
        self.on_side_menu_item_clicked(self.view.sideMenu.item(1))
        self.view.sideMenu.setCurrentRow(1)

        # Use a QTimer to delay the centering by 500 milliseconds
        QTimer.singleShot(500, self.center_on_screen)

        self.processThread = ProcessThread(model)
        self.processThread.finished.connect(self.on_process_thread_finished)

        # CtrlAbilityStateObserver.register(self.view)
        CtrlAbilityStateObserver.register(self)

    def update(self, state):
        if "cam_selected_index" in state:
            # self.model.update_state("cam_selected_index", state["cam_selected_index"])
            # self.stopProcessThread()
            # self.startProcessThread()
            print("===================PROCESS THREAD")
            print(self.processThread.isRunning())
            self.processThread.update_required.emit()
            print("restart process thread")

        print(f"Controller updated with state: {state}")

    # -----------------------------------
    # LOAD/SAVE YAML PROCESS CONFIG FILE
    # -----------------------------------
    def load_file(self):
        # FIX_MK start/stop Thread when new file is loaded
        self.stopProcessThread()
        from ctrlability.core.config_parser import ConfigParser

        fileName, _ = QFileDialog.getOpenFileName(self.view, "Open File", "", "CTRLABILITY CONFIG YAML (*.yaml)")
        print(fileName)
        if fileName:
            # Code to handle the file opening
            print(f"Loading {fileName}")
            ConfigParser.CONFIG_PATH = fileName
            self.startProcessThread()

    def save_file(self):
        fileName, _ = QFileDialog.getSaveFileName(self.view, "Save File", "", "All Files (*);;Text Files (*.txt)")
        if fileName:
            # Code to handle the file saving
            print(f"Saving to {fileName}")
            # self.stopProcess()

    # ----------------------------
    # UI Menu Actions
    # ----------------------------
    def on_side_menu_item_clicked(self, item):
        index = self.view.sideMenu.row(item)
        # Uncheck all other items
        for i in range(self.view.sideMenu.count()):
            if i != index:
                self.view.sideMenu.item(i).setCheckState(Qt.CheckState.Unchecked)
        self.view.mainView.display_index(index)

    def show_about_dialog(self):
        QMessageBox.about(self.view, "About", "This is the About dialog.\nAdd information about your application here.")

    def show_help_dialog(self):
        QMessageBox.about(self.view, "Help", "This is the HELP dialog.\nAdd information about your application here.")

    def center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()  # Get screen geometry
        window = self.view.geometry()  # Get window geometry
        self.view.move(
            (screen.width() - window.width()) / 2,
            (screen.height() - window.height()) / 2,
        )

    # ----------------------------
    # UI HeadFaceView Actions
    # ----------------------------
    def head_face_view_on_cam_changed(self, index):
        print(f"************************Selected cam index: {index}")
        self.model.update_state("cam_selected_index", index)

    # ----------------------------
    # Thread Actions
    # ----------------------------
    def startProcessThread(self):
        print("Starting process")
        if not self.processThread.isRunning():
            self.processThread.start()

    def stopProcessThread(self):
        print("Stopping process")
        if self.processThread.isRunning():
            self.processThread.terminate()  # or implement a more graceful stop if possible
            self.processThread.wait()

    def on_process_thread_finished(self):
        print("Process finished.")

    def close(self):
        log.debug("Closing the application")
        # Stop the thread safely
        self.processThread.stop()
        # Wait for the thread to finish
        self.processThread.wait()
