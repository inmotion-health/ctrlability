import logging
import re
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

        self.view.mainView.process.clicked.connect(self.toggle_process_thread)
        self.view.sideMenu.itemClicked.connect(self.on_side_menu_item_clicked)

        ## Status Menu actions
        self.view.aboutAction.triggered.connect(self.show_about_dialog)
        self.view.loadAction.triggered.connect(self.load_file)
        self.view.saveAction.triggered.connect(self.save_file)
        self.view.helpAction.triggered.connect(self.show_help_dialog)

        ## HeadFaceView actions
        self.view.mainView.headFaceView.cam_combo_box.currentIndexChanged.connect(self.head_face_view_on_cam_changed)
        self.view.mainView.headFaceView.face_expression_comp1.save_button.clicked.connect(
            self.head_face_view_on_expression1_save
        )
        self.view.mainView.headFaceView.face_expression_comp2.save_button.clicked.connect(
            self.head_face_view_on_expression2_save
        )
        self.view.mainView.headFaceView.face_expression_comp3.save_button.clicked.connect(
            self.head_face_view_on_expression3_save
        )
        self.view.mainView.headFaceView.face_expression_comp4.save_button.clicked.connect(
            self.head_face_view_on_expression4_save
        )
        self.view.mainView.headFaceView.mouse_settings.save_button.clicked.connect(
            self.head_face_view_save_mouse_settings
        )
        self.view.mainView.headFaceView.mouse_settings.mode.currentIndexChanged.connect(
            self.head_face_view_mouse_settings_on_mode_changed
        )

        self.model.load_state()
        self.view.update(self.model.state)
        # self.update(self.model.state)

        # select HeadFaceView in the side menu as the default view
        self.on_side_menu_item_clicked(self.view.sideMenu.item(1))
        self.view.sideMenu.setCurrentRow(1)

        # Use a QTimer to delay the centering by 500 milliseconds
        QTimer.singleShot(500, self.center_on_screen)

        self.processThread = ProcessThread(model)
        self.processThread.finished.connect(self.on_process_thread_finished)
        self.processThread.new_frame.connect(self.on_new_frame)
        self.processThread.expressions.connect(self.on_expression_update)

        # CtrlAbilityStateObserver.register(self.view)
        CtrlAbilityStateObserver.register(self)

    def update(self, state):
        if "cam_selected_index" in state:
            log.debug("ctrlability_controller – update – cam_selected_index")
            # self.model.update_state("cam_selected_index", state["cam_selected_index"])
            # self.stopProcessThread()
            # self.startProcessThread()

        self.processThread.update_required.emit()
        log.debug(f"Update Processing and State: {state}")

    # -----------------------------------
    # LOAD/SAVE YAML PROCESS CONFIG FILE
    # -----------------------------------
    def load_file(self):
        # FIX_MK start/stop Thread when new file is loaded
        self.stopProcessThread()
        from ctrlability.core.config_parser import ConfigParser

        fileName, _ = QFileDialog.getOpenFileName(self.view, "Open File", "", "CTRLABILITY CONFIG YAML (*.yaml)")
        if fileName:
            # Code to handle the file opening
            log.debug(f"Loading {fileName}")
            ConfigParser.CONFIG_PATH = fileName
            self.model.load_state()
            for key, value in self.model.state.items():
                if key == "head_face":
                    for k, v in value.items():
                        if k == "cam_selected_index":
                            self.view.mainView.headFaceView.cam_combo_box.setCurrentIndex(v)
                        elif k == "mouse_settings":
                            self.view.mainView.headFaceView.mouse_settings.mode.setCurrentText(v[0])
                            self.view.mainView.headFaceView.mouse_settings.x_threshold.setText(v[1])
                            self.view.mainView.headFaceView.mouse_settings.y_threshold.setText(v[2])
                            self.view.mainView.headFaceView.mouse_settings.x_velocity.setText(v[3])
                            self.view.mainView.headFaceView.mouse_settings.y_velocity.setText(v[4])
                        elif "expression" in k:
                            index = int(k.split("_")[1]) - 1
                            self.view.mainView.headFaceView.expressions[index].expression_dropdown.setCurrentText(v[0])
                            self.view.mainView.headFaceView.expressions[index].threshold.setValue(v[1] * 100)
                            self.view.mainView.headFaceView.expressions[index].action_type.setCurrentText(v[2][0])
                            if v[2][1].__class__ == str:
                                self.view.mainView.headFaceView.expressions[index].action_text_field.setText(v[2][1])
                            else:
                                cmd = ""
                                for k in v[2][1]:
                                    cmd += k + ","
                                cmd = cmd[:-1]
                                self.view.mainView.headFaceView.expressions[index].action_text_field.setText(str(cmd))
            self.startProcessThread()

    def save_file(self):
        fileName, _ = QFileDialog.getSaveFileName(self.view, "Save File", "", "All Files (*);;Text Files (*.txt)")
        if fileName:
            # FIX_MK Code to handle the file saving
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
    # UI Preference View Actions
    # ----------------------------
    def toggle_process_thread(self, checked):
        log.debug("Toggle process thread")
        if self.processThread.isRunning():
            if checked:
                self.processThread.resume()
            else:
                self.processThread.pause()

            self.head_face_view_mouse_settings_on_mode_changed

    def head_face_view_mouse_settings_on_mode_changed(self, index):
        if index == 0:
            self.view.mainView.headFaceView.mouse_settings.x_threshold.setEnabled(True)
            self.view.mainView.headFaceView.mouse_settings.y_threshold.setEnabled(True)
            self.view.mainView.headFaceView.mouse_settings.x_velocity.setEnabled(True)
            self.view.mainView.headFaceView.mouse_settings.y_velocity.setEnabled(True)
        elif index == 1:
            self.view.mainView.headFaceView.mouse_settings.x_threshold.setEnabled(False)
            self.view.mainView.headFaceView.mouse_settings.y_threshold.setEnabled(False)
            self.view.mainView.headFaceView.mouse_settings.x_velocity.setEnabled(False)
            self.view.mainView.headFaceView.mouse_settings.y_velocity.setEnabled(False)

    def head_face_view_save_mouse_settings(self):
        log.debug("Save mouse settings clicked")
        mode = self.view.mainView.headFaceView.mouse_settings.mode.currentText()
        x_threshold = self.view.mainView.headFaceView.mouse_settings.x_threshold.text()
        y_threshold = self.view.mainView.headFaceView.mouse_settings.y_threshold.text()
        x_velocity = self.view.mainView.headFaceView.mouse_settings.x_velocity.text()
        y_velocity = self.view.mainView.headFaceView.mouse_settings.y_velocity.text()
        self.model.update_state("head_face", "mouse_settings", [mode, x_threshold, y_threshold, x_velocity, y_velocity])

    # ----------------------------
    # UI HeadFace View Actions
    # ----------------------------
    def head_face_view_on_cam_changed(self, index):
        log.debug(f"-------------------------------Selected cam index: {index}")
        self.model.update_state("head_face", "cam_selected_index", index)

    # ------ EXPRESSIONS ------
    def save_expression(self, component, expression_key):
        log.debug(f"{expression_key} save clicked")
        expression = component.expression_dropdown.currentText()
        threshold = component.threshold.value() / 100
        action_type = component.action_type.currentText()
        text_field = component.action_text_field.text()

        if action_type == "key":
            cmd = [item.strip() for item in re.split(",", text_field)]  # remove whitespaces and split by comma
        else:
            cmd = text_field.strip()

        action = [action_type, cmd]
        log.debug(f"{expression_key} save: {expression}, {threshold}, {action}")
        self.model.update_state("head_face", expression_key, [expression, threshold, action])

    def head_face_view_on_expression1_save(self, index):
        component = self.view.mainView.headFaceView.face_expression_comp1
        self.save_expression(component, "expression_1")

    def head_face_view_on_expression2_save(self, index):
        component = self.view.mainView.headFaceView.face_expression_comp2
        self.save_expression(component, "expression_2")

    def head_face_view_on_expression3_save(self, index):
        component = self.view.mainView.headFaceView.face_expression_comp3
        self.save_expression(component, "expression_3")

    def head_face_view_on_expression4_save(self, index):
        component = self.view.mainView.headFaceView.face_expression_comp4
        self.save_expression(component, "expression_4")

    # ----------------------------
    # Thread Actions
    # ----------------------------
    def startProcessThread(self):
        log.info("Starting process")
        if not self.processThread.isRunning():
            self.processThread.start()

    def stopProcessThread(self):
        log.info("Stopping process")
        if self.processThread.isRunning():
            self.processThread.terminate()  # or implement a more graceful stop if possible
            self.processThread.wait()

    def on_process_thread_finished(self):
        log.info("Process finished.")

    def close(self):
        log.info("Closing the application")
        # Stop the thread safely
        self.processThread.stop()
        # Wait for the thread to finish
        self.processThread.wait()

    # ----------------------------
    # Get called from Thread via Signals
    # ----------------------------
    def on_new_frame(self, frame):
        self.view.mainView.headFaceView.set_frame(frame)

    def on_expression_update(self, score1, score2, score3, score4):
        self.view.mainView.headFaceView.set_expression_scores(score1, score2, score3, score4)
