import re
import subprocess
import logging as log
from ctrlability.video.platforms import platform
from typing import Dict, List, Optional


def _run_ffmpeg() -> str:
    try:
        output = subprocess.check_output(
            ["ffmpeg", "-f", platform.get_video_format(), "-list_devices", "true", "-i", ""],
            stderr=subprocess.STDOUT,
        ).decode("utf-8")
    except subprocess.CalledProcessError as e:
        output = e.output.decode("utf-8")
    return output


# TODO: this here is still platform dependent, we need to find a way to make it platform independent
def _parse_output(lines: List[str]) -> Dict[int, str]:
    # Find the line that contains 'AVFoundation video devices'
    start_index = next(
        (i for i, line in enumerate(lines) if "AVFoundation video devices" in line),
        None,
    )

    # Find the line that contains 'AVFoundation audio devices'
    end_index = next(
        (i for i, line in enumerate(lines) if "AVFoundation audio devices" in line),
        None,
    )

    # If start_index or end_index is None, then the required lines were not found in the output
    if start_index is None or end_index is None:
        video_devices = {}

        log.warning("Could not find video devices")
    else:
        # Extract the lines that contain the video devices
        video_lines = lines[start_index + 1 : end_index]

        video_devices = {}
        pattern = re.compile(r"\[(\d+)\] (.+)")

        # Iterate over the video lines
        for line in video_lines:
            match = re.search(pattern, line)
            if match and "Capture screen" not in match.group(2):  # Ignore screen capture devices
                device_id = int(match.group(1))
                device_name = match.group(2)
                video_devices[device_id] = device_name

        log.debug(f"Found video devices: {video_devices}")
    return video_devices


def get_available_vidsources():
    output = _run_ffmpeg()
    ffmpeg_output_lines = output.split("\n")

    return _parse_output(ffmpeg_output_lines)
