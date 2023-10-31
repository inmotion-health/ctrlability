import cv2
import mediapipe as mp
import numpy as np
import pyautogui as pag
from one_euro_filter import OneEuroFilter
from videosource import WebcamSource

from face_geometry import (  # isort:skip
    PCF,
    get_metric_landmarks,
    procrustes_landmark_basis,
)

pag.FAILSAFE = False
pag.PAUSE = 0.0
pag.DARWIN_CATCH_UP_TIME = 0.00

mp_drawing = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh
mp_face_mesh_connections = mp.solutions.face_mesh_connections
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=3)

points_idx = [33, 263, 61, 291, 199]
points_idx = points_idx + [key for (key, val) in procrustes_landmark_basis]
points_idx = list(set(points_idx))
points_idx.sort()

# uncomment next line to use all points for PnP algorithm
# points_idx = list(range(0,468)); points_idx[0:2] = points_idx[0:2:-1];

frame_height, frame_width, channels = (720, 1280, 3)

# pseudo camera internals
focal_length = frame_width
center = (frame_width / 2, frame_height / 2)
camera_matrix = np.array(
    [[focal_length, 0, center[0]], [0, focal_length, center[1]], [0, 0, 1]],
    dtype="double",
)

dist_coeff = np.zeros((4, 1))

# get screen size
screenWidth, screenHeight = pag.size()


def main():
    source = WebcamSource()

    refine_landmarks = True

    pcf = PCF(
        near=1,
        far=10000,
        frame_height=frame_height,
        frame_width=frame_width,
        fy=camera_matrix[1, 1],
    )

    oef_1 = OneEuroFilter(t0=0, x0=0, min_cutoff=0.01, beta=0.005)
    oef_2 = OneEuroFilter(t0=0, x0=0, min_cutoff=0.001, beta=0.001)

    with mp_face_mesh.FaceMesh(
        static_image_mode=False,
        refine_landmarks=refine_landmarks,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as face_mesh:
        for idx, (frame, frame_rgb) in enumerate(source):
            results = face_mesh.process(frame_rgb)
            multi_face_landmarks = results.multi_face_landmarks

            if multi_face_landmarks:
                face_landmarks = multi_face_landmarks[0]
                landmarks = np.array([(lm.x, lm.y, lm.z) for lm in face_landmarks.landmark])
                # print(landmarks.shape)
                landmarks = landmarks.T

                if refine_landmarks:
                    landmarks = landmarks[:, :468]

                metric_landmarks, pose_transform_mat = get_metric_landmarks(landmarks.copy(), pcf)

                image_points = landmarks[0:2, points_idx].T * np.array([frame_width, frame_height])[None, :]
                model_points = metric_landmarks[0:3, points_idx].T

                # see here:
                # https://github.com/google/mediapipe/issues/1379#issuecomment-752534379
                pose_transform_mat[1:3, :] = -pose_transform_mat[1:3, :]
                mp_rotation_vector, _ = cv2.Rodrigues(pose_transform_mat[:3, :3])
                mp_translation_vector = pose_transform_mat[:3, 3, None]

                if False:
                    # sanity check
                    # get same result with solvePnP

                    success, rotation_vector, translation_vector = cv2.solvePnP(
                        model_points,
                        image_points,
                        camera_matrix,
                        dist_coeff,
                        flags=cv2.cv2.SOLVEPNP_ITERATIVE,
                    )

                    np.testing.assert_almost_equal(mp_rotation_vector, rotation_vector)
                    np.testing.assert_almost_equal(mp_translation_vector, translation_vector)

                for face_landmarks in multi_face_landmarks:
                    mp_drawing.draw_landmarks(
                        image=frame,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh_connections.FACEMESH_TESSELATION,
                        landmark_drawing_spec=drawing_spec,
                        connection_drawing_spec=drawing_spec,
                    )

                nose_tip = model_points[0]
                nose_tip_extended = 3.5 * nose_tip

                (nose_pointer2D, jacobian) = cv2.projectPoints(
                    np.array([nose_tip, nose_tip_extended]),
                    mp_rotation_vector,
                    mp_translation_vector,
                    camera_matrix,
                    dist_coeff,
                )

                MAGENTA = (255, 0, 255)

                nose_tip_2D, nose_tip_2D_extended = nose_pointer2D.squeeze().astype(int)

                # filter nose tip
                nose_tip_2D_extended = oef_1(idx, nose_tip_2D_extended).astype(int)

                frame = cv2.line(frame, nose_tip_2D, nose_tip_2D_extended, MAGENTA, 2)
                text_pos = (nose_tip_2D_extended[0] + 10, nose_tip_2D_extended[1] + 10)
                cv2.putText(frame, f"{nose_tip_extended}", text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.5, MAGENTA, 1)

                # draw rectangle around nose
                nose = nose_tip_2D
                ratio = 1080 / 1920
                width = 500
                height = int(width * ratio)
                x = nose[0] - width // 2
                y = nose[1] - height // 2
                frame = cv2.rectangle(frame, (x, y), (x + width, y + height), MAGENTA, 2)

                # translate nose tip to the rectangle
                translated_nose_tip = nose_tip_2D_extended - np.array([x, y])
                translated_nose_tip = translated_nose_tip / np.array([width, height])

                # scale nose tip to screen size
                translated_nose_tip = translated_nose_tip * np.array([screenWidth, screenHeight])

                # filter the translated nose tip
                translated_nose_tip = oef_2(idx, translated_nose_tip).astype(int)

                # clip to screen size
                translated_nose_tip = np.clip(translated_nose_tip, [0, 0], [screenWidth, screenHeight])

                # move mouse
                pag.moveTo(*translated_nose_tip, duration=0.1)

            source.show(frame)


if __name__ == "__main__":
    main()
