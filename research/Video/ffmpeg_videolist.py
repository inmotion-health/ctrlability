import subprocess
import re

# Run the ffmpeg command and capture its output
try:
    output = subprocess.check_output(
        ["ffmpeg", "-f", "avfoundation", "-list_devices", "true", "-i", ""],
        stderr=subprocess.STDOUT,
    ).decode("utf-8")
except subprocess.CalledProcessError as e:
    output = e.output.decode("utf-8")

# Split the output into lines
lines = output.split("\n")

# Find the line that contains 'AVFoundation video devices'
start_index = next(
    (i for i, line in enumerate(lines) if "AVFoundation video devices" in line), None
)

# Find the line that contains 'AVFoundation audio devices'
end_index = next(
    (i for i, line in enumerate(lines) if "AVFoundation audio devices" in line), None
)

# If start_index or end_index is None, then the required lines were not found in the output
if start_index is None or end_index is None:
    video_devices = {}
else:
    # Extract the lines that contain the video devices
    video_lines = lines[start_index + 1 : end_index]

    # Initialize an empty dictionary to store the video devices
    video_devices = {}

    # Define the regex pattern to match the ID and name
    pattern = re.compile(r"(\d+)\.\s(.+)")

    # Iterate over the video lines
    for line in video_lines:
        match = re.search(r"\[(\d+)\] (.+)", line)
        if match:
            device_id = int(match.group(1))
            device_name = match.group(2)
            video_devices[device_id] = device_name


# Print the video devices
print(video_devices[0])
