import logging
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QVBoxLayout, QHBoxLayout, QWidget, QFrame
from ctrlability_ui.views.cam_roi_component import CamRoiComponent
from ctrlability_ui.views.facial_expression_component import FacialExpressionComponent

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

        self.cam_roi_region = CamRoiComponent()
        self.cam_roi_region.setFixedSize(480, 270)

        center_layout = QHBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(self.cam_roi_region)
        center_layout.addStretch()
        layout.addLayout(center_layout)

        # Line separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # Create instances of FacialExpressionComponent
        self.face_expression_comp1 = FacialExpressionComponent()
        self.face_expression_comp2 = FacialExpressionComponent()
        self.face_expression_comp3 = FacialExpressionComponent()
        self.face_expression_comp4 = FacialExpressionComponent()

        # First row of face_expression components
        first_row_layout = QHBoxLayout()
        first_row_layout.addWidget(self.face_expression_comp1)
        first_row_layout.addWidget(self.face_expression_comp2)

        # Second row of face_expression components
        second_row_layout = QHBoxLayout()
        second_row_layout.addWidget(self.face_expression_comp3)
        second_row_layout.addWidget(self.face_expression_comp4)

        # Add the rows to the main layout
        layout.addLayout(first_row_layout)
        layout.addLayout(second_row_layout)
        # Add sliders
        # for i in range(3):
        #    layout.addWidget(QSlider())
