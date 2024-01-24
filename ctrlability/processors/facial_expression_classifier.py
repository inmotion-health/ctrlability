import os
import urllib.request

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from ctrlability.core import Processor, MappingEngine, bootstrapper


@bootstrapper.add()
class FacialExpressionClassifier(Processor):
    def __init__(self, mapping_engine: MappingEngine, min_confidence=0):
        super().__init__(mapping_engine)

        self.min_confidence = min_confidence

        dirname = os.path.dirname(__file__)
        self.model_file = os.path.join(dirname, "face_landmarker_v2_with_blendshapes.task")

        if not os.path.isfile(self.model_file):
            url = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
            urllib.request.urlretrieve(url, self.model_file)

        base_options = python.BaseOptions(model_asset_path=self.model_file)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            output_face_blendshapes=True,
            output_facial_transformation_matrixes=True,
            num_faces=1,
        )
        self.detector = vision.FaceLandmarker.create_from_options(options)

    def compute(self, image):
        shapes = []
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)
        detection_result = self.detector.detect(image)

        if detection_result.face_blendshapes and detection_result.face_landmarks:
            if detection_result.face_blendshapes[0] and detection_result.face_landmarks[0]:
                for shape in detection_result.face_blendshapes[0]:
                    if shape.score > self.min_confidence:
                        shapes.append(shape)

        return [shapes, detection_result.face_landmarks[0]]
