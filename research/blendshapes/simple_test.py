import os

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from vidcontrol import VideoManager
import urllib.request


# get path relative to this file
dirname = os.path.dirname(__file__)
model_file = os.path.join(dirname, "face_landmarker_v2_with_blendshapes.task")

# check if the model file exists and download it if not
if not os.path.isfile(model_file):
    # download the model file
    url = (
        "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
    )
    urllib.request.urlretrieve(url, model_file)

base_options = python.BaseOptions(model_asset_path=model_file)
options = vision.FaceLandmarkerOptions(
    base_options=base_options, output_face_blendshapes=True, output_facial_transformation_matrixes=True, num_faces=1
)
detector = vision.FaceLandmarker.create_from_options(options)


manager = VideoManager()

source = manager.get_video_source(0)

for frame in source:
    image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
    detection_result = detector.detect(image)

    if detection_result.face_blendshapes[0]:
        for shape in detection_result.face_blendshapes[0]:
            if shape.score > 0.5:
                # put name of shape on image
                cv2.putText(
                    frame,
                    shape.category_name,
                    (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1,
                )

    # convert to BGR
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    cv2.imshow("frame", frame)
    key = cv2.waitKey(1)  # Wait for 1 millisecond
    if key == 27:  # Exit loop on 'Esc' key press
        break

cv2.destroyAllWindows()
