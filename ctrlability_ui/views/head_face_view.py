import logging
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QFrame,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
    QDialog,
    QLabel,
)
from ctrlability_ui.views.cam_roi_component import CamRoiComponent
from ctrlability_ui.views.facial_expression_component import FacialExpressionComponent

log = logging.getLogger(__name__)


class CollapsibleSection(QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        self.toggleButton = QPushButton(title)
        self.toggleButton.setCheckable(True)
        self.toggleButton.setChecked(False)
        # self.toggleButton.setEnabled(False)
        self.toggleButton.clicked.connect(self.toggle)

        self.contentArea = QFrame()
        self.contentArea.setMaximumHeight(0)
        self.contentArea.setVisible(False)

        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.layout.addWidget(self.toggleButton)
        self.layout.addWidget(self.contentArea)

    def toggle(self):
        self.contentArea.setVisible(self.toggleButton.isChecked())
        self.contentArea.setMaximumHeight(16777215 if self.toggleButton.isChecked() else 0)


class CamRoiWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cam ROI")
        self.setLayout(QVBoxLayout())
        self.camRoiComponent = CamRoiComponent()
        self.camRoiComponent.setFixedSize(480, 270)
        self.layout().addWidget(self.camRoiComponent)
        # Set additional window flags if needed, e.g., for a floating window
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)


class HeadFaceView(QWidget):

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(2)

        # FIX_MK: SUB_MENU STYLE
        # sub_menu_layout = QHBoxLayout(self)
        # self.facial_expressions_button = QPushButton("FACIAL EXPRESSIONS")
        # self.facial_expressions_button.setCheckable(True)
        # # self.facial_expressions_button.setFixedWidth(250)
        # sub_menu_layout.addWidget(self.facial_expressions_button)
        # self.facial_expressions_button.clicked.connect(self.toggle_facial_expressions)

        # self.landmark_distance_button = QPushButton("LANDMARK DISTANCES")
        # self.landmark_distance_button.setCheckable(True)
        # # self.landmark_distance_button.setFixedWidth(250)
        # sub_menu_layout.addWidget(self.landmark_distance_button)
        # self.landmark_distance_button.clicked.connect(self.toggle_landmark_distance)

        # self.roi_button = QPushButton("ROI`S")
        # self.roi_button.setCheckable(True)
        # # self.roi_button.setFixedWidth(2)
        # sub_menu_layout.addWidget(self.roi_button)
        # self.roi_button.clicked.connect(self.toggle_roi)
        # layout.addLayout(sub_menu_layout)

        # # Line separator
        # line = QFrame()
        # line.setFrameShape(QFrame.HLine)
        # line.setFrameShadow(QFrame.Sunken)
        # layout.addWidget(line)

        cam_setting_layout = QHBoxLayout(self)
        label = QLabel("INPUT:")
        label.setFixedWidth(100)
        cam_setting_layout.addWidget(label)
        self.cam_combo_box = QComboBox(self)
        self.cam_combo_box.addItem("CAM1")
        self.cam_combo_box.addItem("CAM2")
        # self.cam_combo_box.setFixedWidth(250)
        cam_setting_layout.addWidget(self.cam_combo_box)

        # Button to open the CamRoiWindow
        self.openCamRoiWindowButton = QPushButton("SHOW CAM")
        self.openCamRoiWindowButton.setCheckable(True)
        self.openCamRoiWindowButton.setFixedWidth(150)
        cam_setting_layout.addWidget(self.openCamRoiWindowButton)
        self.openCamRoiWindowButton.clicked.connect(self.toggleCamRoiWindow)
        self.camRoiWindow = None
        layout.addLayout(cam_setting_layout)

        # Line separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # Create the collapsible section for the FacialExpressionComponents
        self.facialExpressionSection = CollapsibleSection("FACIAL EXPRESSIONS")
        self.initFacialExpressionComponents()
        layout.addWidget(self.facialExpressionSection)

        # Create the collapsible section for the FacialExpressionComponents
        self.landmark_distance_section = CollapsibleSection("LANDMARK DISTANCES")
        self.init_landmark_distance_components()
        layout.addWidget(self.landmark_distance_section)

        # Create the collapsible section for the FacialExpressionComponents
        self.roi_section = CollapsibleSection("ROI`S")
        self.init_roi_components()
        layout.addWidget(self.roi_section)

        # Add a spacer item at the bottom to push everything up
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)

        # # Create instances of FacialExpressionComponent
        # self.face_expression_comp1 = FacialExpressionComponent()
        # self.face_expression_comp2 = FacialExpressionComponent()
        # self.face_expression_comp3 = FacialExpressionComponent()
        # self.face_expression_comp4 = FacialExpressionComponent()

        # # First row of face_expression components
        # first_row_layout = QHBoxLayout()
        # first_row_layout.addWidget(self.face_expression_comp1)
        # first_row_layout.addWidget(self.face_expression_comp2)

        # # Second row of face_expression components
        # second_row_layout = QHBoxLayout()
        # second_row_layout.addWidget(self.face_expression_comp3)
        # second_row_layout.addWidget(self.face_expression_comp4)

        # # Add the rows to the main layout
        # layout.addLayout(first_row_layout)
        # layout.addLayout(second_row_layout)
        # Add sliders
        # for i in range(3):
        #    layout.addWidget(QSlider())

    def initFacialExpressionComponents(self):
        # Container for the FacialExpressionComponents
        container_widget = QWidget()
        container_layout = QVBoxLayout(container_widget)
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

        # Add the rows to the container layout
        container_layout.addLayout(first_row_layout)
        container_layout.addLayout(second_row_layout)

        # Add the container to the content area of the collapsible section
        self.facialExpressionSection.contentArea.setLayout(container_layout)
        self.facialExpressionSection.contentArea.setMaximumHeight(16777215)  # Ensure it can expand
        self.facialExpressionSection.toggle()  # Optionally start it as expanded

    def init_landmark_distance_components(self):
        log.debug("init_landmark_distance_components")

    def init_roi_components(self):
        log.debug("init_roi_components")

    def openCamRoiWindow(self):
        self.camRoiWindow = CamRoiWindow(self)
        self.camRoiWindow.show()

    def toggleCamRoiWindow(self):
        if self.camRoiWindow is None:  # If the window does not exist, create it
            self.camRoiWindow = CamRoiWindow(self)
            self.camRoiWindow.show()
            self.camRoiWindow.setAttribute(Qt.WA_DeleteOnClose)  # Ensure the window is deleted when closed
            # Connect the window's close event to uncheck the button
            self.camRoiWindow.finished.connect(lambda: self.openCamRoiWindowButton.setChecked(False))
        else:
            # If the window exists, check its visibility to decide whether to show or hide it
            if self.camRoiWindow.isVisible():
                self.camRoiWindow.hide()
                self.openCamRoiWindowButton.setChecked(False)
            else:
                self.camRoiWindow.show()
                self.openCamRoiWindowButton.setChecked(True)

        # Optionally, handle the window's closed event to reset the camRoiWindow reference to None
        self.camRoiWindow.destroyed.connect(self.resetCamRoiWindowReference)

    def resetCamRoiWindowReference(self):
        self.camRoiWindow = None

    def toggle_facial_expressions(self):
        log.debug("toggle_facial_expressions")
        state = self.facial_expressions_button.isChecked()
        self.facialExpressionSection.toggleButton.setChecked(state)
        self.facialExpressionSection.toggle()

    def toggle_landmark_distance(self):
        self.landmark_distance_section.toggle()

    def toggle_roi(self):
        self.roi_section.toggle()
