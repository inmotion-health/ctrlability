import logging

import whispercpp as w

from ctrlability.core import bootstrapper, Stream

log = logging.getLogger(__name__)


@bootstrapper.add()
class WhisperStream(Stream):
    def __init__(self):
        model_name = "tiny"  # Choose the model you want to use
        self.device_id = 0  # Default audio device ID
        length_ms = 5000  # Length of the audio buffer in milliseconds
        sample_rate = w.api.SAMPLE_RATE  # Sample rate of the audio device
        n_threads = 8  # Number of threads for decoding
        step_ms = 2000  # Step size of the audio buffer in milliseconds
        keep_ms = 200  # Length of the audio buffer to keep in milliseconds
        max_tokens = 32  # Maximum number of tokens to decode

        self.iterator = w.Whisper.from_pretrained(model_name).stream_transcribe(
            device_id=self.device_id,
            length_ms=length_ms,
            sample_rate=sample_rate,
            n_threads=n_threads,
            step_ms=step_ms,
            keep_ms=keep_ms,
            max_tokens=max_tokens,
            language="de",
        )

    def get_next(self):
        return next(self.iterator)

    def __repr__(self):
        return f"WhisperStream(device_id: {self.device_id})"
