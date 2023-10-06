import logging as log
import platform
from typing import Optional, Tuple, Dict, List

import ctrlability.video.platforms.base as base

if platform.system() == "Windows":
    from pygrabber.dshow_graph import FilterGraph


class WindowsVideoPlatform(base.VideoPlatform):
    def __init__(self):
        self.graph = FilterGraph()

        print("Initialized WindowsVideoPlatform")

    def get_video_format(self):
        return "dshow"

    def list_video_devices(self) -> Dict[int, str]:
        devices = self.graph.get_input_devices()
        dict_devices = {i: device for i, device in enumerate(devices)}
        log.debug(f"Found video devices: {dict_devices}")
        return dict_devices

    def list_available_resolutions(self, device_id: int) -> Optional[List[Tuple[Tuple[int, int], int]]]:
        self.graph = FilterGraph()  # Resetting the graph to remove the previous device
        self.graph.add_video_input_device(device_id)

        formats = self.graph.get_input_device().get_formats()

        # Extracting resolutions and frame rate from formats
        resolutions = []
        for format_info in formats:
            width, height = format_info.get("width"), format_info.get("height")
            fps = format_info.get("fps", 30)
            resolutions.append(((width, height), fps))

        return resolutions

    def get_ffmpeg_device_name(self, cam_id: int) -> str:
        all_devices = self.list_video_devices()
        return f"<video{cam_id}>"
