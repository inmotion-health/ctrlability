# Streams

## VideoStream
A Stream that captures video from a webcam. It returns the frame from the video stream. Uses vidcontrol for video
capture, which uses ffmpeg.

#### Returns

- **FrameData**: The frame from the video stream.

#### Arguments

| Name | Description |
| ---- | ----------- |
| webcam_id (int) | The ID of the webcam. |
| mirror (bool, optional) | Whether to mirror the video stream. Defaults to True. |
| mirror_horizontal (bool, optional) | Whether to horizontally flip the video stream. Defaults to False. |
| debug (bool, optional) | Whether to enable debug mode. Defaults to False. |
