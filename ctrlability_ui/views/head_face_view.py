import logging
from PySide6.QtWidgets import (
    QComboBox,
    QVBoxLayout,
    QWidget,
)
from ctrlability_ui.views.webcam_roi_widget import WebcamRoiWidget

log = logging.getLogger(__name__)


class HeadFaceView(QWidget):

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        self.cam_combo_box = QComboBox(self)
        self.cam_combo_box.addItem("CAM1")
        self.cam_combo_box.addItem("CAM2")
        # self.cam_combo_box.setFixedWidth(250)
        layout.addWidget(self.cam_combo_box)

        self.webcam_roi_region = WebcamRoiWidget()
        self.webcam_roi_region.setFixedSize(640, 480)
        layout.addWidget(self.webcam_roi_region)

        # Add sliders
        # for i in range(3):
        #    layout.addWidget(QSlider())
