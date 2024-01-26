import cv2
import numpy as np

from ctrlability.core import Processor, bootstrapper, MappingEngine
from ctrlability.core.data_types import LandmarkData, NormalVectorData
from ctrlability.helpers.mousectrl import MouseCtrl
from ctrlability.math.face_geometry import procrustes_landmark_basis, PCF, get_metric_landmarks


@bootstrapper.add()
class LandmarkNormalVector(Processor):
    def __init__(self, mapping_engine: MappingEngine, landmark, ref_landmarks, tip_scale=3.5):
        super().__init__(mapping_engine)
        self.landmark = landmark
        self.tip_scale = tip_scale

        self.dist_coefficient = np.zeros((4, 1))

        # prepare reference landmarks and add procrustes landmarks
        self.ref_landmarks = ref_landmarks + [key for (key, val) in procrustes_landmark_basis]
        self.ref_landmarks = list(set(self.ref_landmarks))
        self.ref_landmarks.sort()

        # add datafields we need to fill once the first frame comes in
        self.frame_width = None
        self.frame_height = None
        self.channels = 3

        self.pcf = None
        self.camera_matrix = None
        self.center = None

        self.screen_width, self.screen_height = MouseCtrl.screen_width, MouseCtrl.screen_height

    def compute(self, landmark_data: LandmarkData):
        if landmark_data is None:
            return

        # if we get data for the first time, let's store the frame size and do some more initializing
        if self.frame_width is None or self.frame_height is None:
            self.frame_width = landmark_data.width
            self.frame_height = landmark_data.height

            self.init_pseudo_camera()
            self.setup_pcf_and_filters()

        landmarks = np.array([(lm.x, lm.y, lm.z) for lm in landmark_data.landmarks])
        landmarks = landmarks.T
        landmarks = landmarks[:, :468]

        metric_landmarks, pose_transform_mat = get_metric_landmarks(landmarks.copy(), self.pcf)

        model_points = metric_landmarks[0:3, self.ref_landmarks].T

        pose_transform_mat[1:3, :] = -pose_transform_mat[1:3, :]
        mp_rotation_vector, _ = cv2.Rodrigues(pose_transform_mat[:3, :3])
        mp_translation_vector = pose_transform_mat[:3, 3, None]

        nose_tip = model_points[0]
        nose_tip_extended = self.tip_scale * nose_tip

        (nose_pointer2D, jacobian) = cv2.projectPoints(
            np.array([nose_tip, nose_tip_extended]),
            mp_rotation_vector,
            mp_translation_vector,
            self.camera_matrix,
            self.dist_coefficient,
        )

        nose_tip_2d, nose_tip_2d_extended = nose_pointer2D.squeeze()

        # normalize nose tip coordinates to screen size
        nose_tip_2d[0] = nose_tip_2d[0] / self.frame_width
        nose_tip_2d[1] = nose_tip_2d[1] / self.frame_height
        nose_tip_2d_extended[0] = nose_tip_2d_extended[0] / self.frame_width
        nose_tip_2d_extended[1] = nose_tip_2d_extended[1] / self.frame_height

        return NormalVectorData(
            nose_tip_2d, nose_tip_2d_extended, landmark_data.landmarks, self.frame_width, self.frame_height
        )

    def init_pseudo_camera(self):
        focal_length = self.frame_width
        self.center = (self.frame_width / 2, self.frame_height / 2)
        self.camera_matrix = np.array(
            [[focal_length, 0, self.center[0]], [0, focal_length, self.center[1]], [0, 0, 1]],
            dtype="double",
        )

    def setup_pcf_and_filters(self):
        self.pcf = PCF(
            near=1,
            far=10000,
            frame_height=self.frame_height,
            frame_width=self.frame_width,
            fy=self.camera_matrix[1, 1],
        )
