import platform
from abc import ABC, abstractmethod


class _VideoPlatform:
    """
    Abstract base class for video platforms.
    """

    @abstractmethod
    def get_video_format(self) -> str:
        """
        Returns the video format for the platform.
        """
        pass


class MacVideoPlatform(_VideoPlatform):
    def get_video_format(self):
        return "avfoundation"


class WindowsVideoPlatform(_VideoPlatform):
    def get_video_format(self):
        return "dshow"


class LinuxVideoPlatform(_VideoPlatform):
    def get_video_format(self):
        return "v4l2"


class VideoPlatformFactory:
    """
    A factory class for creating video platforms based on the current system.

    Usage:
    platform = VideoPlatformFactory.make_platform()
    platform.play_video("example.mp4")
    """

    @staticmethod
    def make_platform():
        system = platform.system()
        if system == "Darwin":
            return MacVideoPlatform()
        elif system == "Windows":
            return WindowsVideoPlatform()
        elif system == "Linux":
            return LinuxVideoPlatform()
        else:
            raise Exception("Unsupported platform")


# static instance
platform = VideoPlatformFactory.make_platform()
