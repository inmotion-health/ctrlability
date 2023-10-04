import logging as log
import re
from typing import Dict, Optional, Tuple, List

import ctrlability.util.subprocess as subprocess
import ctrlability.video.platforms.base as base


class MacVideoPlatform(base.VideoPlatform):
    def get_video_format(self):
        return "avfoundation"

    def list_video_devices(self) -> Dict[int, str]:
        output = subprocess.get_cmd_output(["ffmpeg", "-f", self.get_video_format(), "-list_devices", "true", "-i", ""])

        if output == "":
            raise Exception("No output from ffmpeg")

        return self._parse_device_list(output)

    @staticmethod
    def _parse_device_list(output: str) -> Dict[int, str]:
        lines = output.split("\n")

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

    def list_available_resolutions(self, device_id: int) -> Optional[list[Tuple[Tuple[int, int], int]]]:
        output = subprocess.get_cmd_output(
            [
                "ffmpeg",
                "-f",
                self.get_video_format(),
                "-video_size",
                "123x456",
                "-i",
                f"{device_id}",
                "-t",
                "1",
                "-f",
                "null",
                "-",
            ]
        )
        if output == "":
            raise Exception("No output from ffmpeg")

        return self._parse_resolutions(output)

    @staticmethod
    def _parse_resolutions(resolution: str) -> List[Tuple[Tuple[int, int], int]]:
        pattern = re.compile(r"(\d+x\d+)@\[\d+\.\d+\s+(\d+\.\d+)\]fps")
        matches = pattern.findall(resolution)
        resolutions = []

        for width_str, fps_str in matches:
            width, height = map(int, width_str.split("x"))
            fps = round(float(fps_str))
            resolutions.append(((width, height), fps))

        return resolutions
