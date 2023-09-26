import subprocess
import re


def get_available_resolutions(camera_id):
    output = _run_ffmpeg(camera_id)
    resolutions = _parse_output(output)
    return _parse_into_tuples(resolutions)


def _run_ffmpeg(camera_id):
    try:
        output = subprocess.check_output(
            [
                "ffmpeg",
                "-f",
                "avfoundation",
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


def _parse_output(output):
    pattern = re.compile(r"(\d+x\d+)@\[\d+\.\d+\s+(\d+\.\d+)\]fps")
    matches = pattern.findall(output)

    return matches


def _parse_into_tuples(matches):
    pattern = re.compile(r"(\d+)x(\d+)")
    resolutions = []

    for match in matches:
        resolution = pattern.findall(match[0])

        # Convert the resolution to a tuple of ints
        resolution = tuple(map(int, resolution[0]))
        fps = round(float(match[1]))

        resolutions.append((resolution, fps))

    return resolutions


def find_best_resolution(camera_id):
    resolutions = get_available_resolutions(camera_id)

    if len(resolutions) == 0:
        return None

    # find 720p resolutions
    _720_resolutions = [t for t in resolutions if t[0][1] == 720]

    if len(_720_resolutions) == 0:
        return resolutions[0]

    resolution = _720_resolutions[0][0]
    fps = _720_resolutions[0][1]

    return (resolution, fps)
