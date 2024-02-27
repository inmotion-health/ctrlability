import sounddevice as sd

from whisper_online import FasterWhisperASR, OnlineASRProcessor  # Assuming these are in your path

src_lan = "en"  # Source language
tgt_lan = "en"  # Target language

# Initialize the ASR model
asr = FasterWhisperASR(src_lan, "large-v2", device="cpu")  # Adjust according to actual import and class initialization

# Create the online processing object
online = OnlineASRProcessor(asr)


def audio_callback(indata, frames, time, status):
    """
    This callback function is called by sounddevice for each audio chunk (block) received from the microphone.
    """
    if status:
        print(status)  # Print any errors

    # Convert the input data to a 1D numpy array (from 2D)
    audio_chunk = indata[:, 0]

    # Insert and process the current audio chunk
    online.insert_audio_chunk(audio_chunk)
    o = online.process_iter()
    print(o)  # do something with current partial output


# Define microphone recording parameters
samplerate = 16000  # Whisper models work with 16kHz audio
channels = 1  # Mono audio
blocksize = int(samplerate * 5)  # Define block size (e.g., 5 seconds per chunk)

try:
    # Start recording from the microphone
    with sd.InputStream(callback=audio_callback, samplerate=samplerate, channels=channels, blocksize=blocksize):
        print("Recording... Press Ctrl+C to stop.")
        sd.sleep(60000)  # Record for 60 seconds or until Ctrl+C is pressed
except KeyboardInterrupt:
    print("Recording stopped")
except Exception as e:
    print(str(e))

# At the end of audio processing
o = online.finish()
print(o)  # do something with the last output

# Refresh if you're going to re-use the object for the next audio
online.init()
