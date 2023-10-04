import importlib

from ctrlability.video.platforms.linux import LinuxVideoPlatform
from ctrlability.video.platforms.mac import MacVideoPlatform
from ctrlability.video.platforms.win import WindowsVideoPlatform

std_platform = importlib.import_module("platform")


def get_platform():
    system = std_platform.system()
    if system == "Darwin":
        return MacVideoPlatform()
    elif system == "Windows":
        return WindowsVideoPlatform()
    elif system == "Linux":
        return LinuxVideoPlatform()
    else:
        raise Exception("Unsupported platform")


platform = get_platform()
