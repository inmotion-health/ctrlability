import subprocess


def check_resolution(device, width, height):
    output = subprocess.check_output(
        ["ffmpeg", "-f", "avfoundation", "-s", f"{width}x{height}", "-i", device],
        stderr=subprocess.STDOUT,
    ).decode("utf-8")


# Usage
device = "<video0>"
width = 640
height = 480
check_resolution(device, width, height)
