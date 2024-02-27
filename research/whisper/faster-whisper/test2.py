import os
import wave

import pyaudio
from faster_whisper import WhisperModel

NEON_GREEN = "\033[92m"
RESET_COLOR = "\033[0m"

BUFFER_SIZE = 4096 * 4
FRAMES_PER_BUFFER = 16000


def transcribe_chunk(model, file_path):
    segments, info = model.transcribe(file_path, beam_size=5, language="de")
    transcription = " ".join(segment.text for segment in segments)
    return transcription


def record_chunk(p, stream, file_path, chunk_length=1):
    frames = []
    for _ in range(0, int(16000 / BUFFER_SIZE * chunk_length)):
        try:
            data = stream.read(BUFFER_SIZE)
            frames.append(data)
        except IOError as e:
            # Handle buffer overflow here
            print("Buffer overflow: ", e)

    wf = wave.open(file_path, "wb")
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(FRAMES_PER_BUFFER)
    wf.writeframes(b"".join(frames))
    wf.close()


def main2():
    # Choose your model settings
    model_size = "small"
    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16, channels=1, rate=FRAMES_PER_BUFFER, input=True, frames_per_buffer=BUFFER_SIZE
    )

    accumulated_transcription = ""  # Initialize an empty string to accumulate transcriptions

    try:
        while True:
            chunk_file = "temp_chunk.wav"
            record_chunk(p, stream, chunk_file)
            transcription = transcribe_chunk(model, chunk_file)
            print(NEON_GREEN + transcription + RESET_COLOR)
            os.remove(chunk_file)

            # Append the new transcription to the accumulated transcription
            accumulated_transcription += transcription + " "

    except KeyboardInterrupt:
        print("Stopping...")
        # Write the accumulated transcription to the log file
        with open("log.txt", "w") as log_file:
            log_file.write(accumulated_transcription)
    finally:
        print("LOG:" + accumulated_transcription)
        stream.stop_stream()
        stream.close()
        p.terminate()


if __name__ == "__main__":
    main2()
