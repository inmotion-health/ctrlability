from uuid import uuid4

from ctrlability.actions import Logger
from ctrlability.core import MappingEngine
from ctrlability.core.stream_handler import StreamHandler
from ctrlability.processors import FaceLandmarkProcessor
from ctrlability.streams import VideoStream
from ctrlability.triggers import LandmarkDistance

stream_handlers = []
mapping_engine = MappingEngine()

# create a video stream
vid_stream = VideoStream(0, mirror=True, debug=True)
vid_stream_handler = StreamHandler(vid_stream, mapping_engine)
stream_handlers.append(vid_stream_handler)

# create a face landmark processor
face_landmarks = FaceLandmarkProcessor(mapping_engine)
vid_stream_handler.connect_post_processor(face_landmarks)

# create a trigger and connect it to an action
mouth_open_trigger = LandmarkDistance(landmarks=[12, 15], threshold=0.2, direction="greater")
action_id, action = uuid4(), Logger()
face_landmarks.connect_trigger(mouth_open_trigger, mapping_engine.register(action_id, action))


def main():
    while True:
        try:
            for stream_handler in stream_handlers:
                stream_handler.process(None)
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
