import subprocess
import re
from typing import List, Tuple, Optional

from ctrlability.video.platforms import platform

PREFERRED_HEIGHT = 720


def get_available_resolutions(camera_id: int) -> List[Tuple[Tuple[int, int], int]]:
    output = _run_ffmpeg(camera_id)
    resolutions = _parse_output(output)
    return _parse_into_tuples(resolutions)


def _run_ffmpeg(camera_id: int) -> str:
    try:
        output = subprocess.check_output(
            [
                "ffmpeg",
                "-f",
                platform.get_video_format(),
                "-video_size",
                "123x456",
                "-i",
                f"{camera_id}",
                "-t",
                "1",
                "-f",
                "null",
                "-",
            ],
            stderr=subprocess.STDOUT,
        ).decode("utf-8")
    except subprocess.CalledProcessError as e:
        output = e.output.decode("utf-8")
    return output


def _parse_output(output: str) -> List[Tuple[str, str]]:
    pattern = re.compile(r"(\d+x\d+)@\[\d+\.\d+\s+(\d+\.\d+)\]fps")
    return pattern.findall(output)


def _parse_into_tuples(matches: List[Tuple[str, str]]) -> List[Tuple[Tuple[int, int], int]]:
    resolutions = []

    for width_str, fps_str in matches:
        width, height = map(int, width_str.split("x"))
        fps = round(float(fps_str))
        resolutions.append(((width, height), fps))

    return resolutions


def find_best_resolution(camera_id: int) -> Optional[Tuple[Tuple[int, int], int]]:
    resolutions = get_available_resolutions(camera_id)

    if not resolutions:
        return None, None

    # Find 720p resolutions
    _720_resolutions = [res for res in resolutions if res[0][1] == PREFERRED_HEIGHT]

    if not _720_resolutions:
        return resolutions[0][0], resolutions[0][1]

    return _720_resolutions[0][0], _720_resolutions[0][1]
