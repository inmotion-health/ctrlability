from typing import Optional, Tuple, Dict
import logging as log

import ctrlability.video.platforms.base as base


class LinuxVideoPlatform(base.VideoPlatform):
    def __init__(self):
        print("Initialized LinuxVideoPlatform")

    def get_video_format(self):
        return "v4l2"

    def list_video_devices(self) -> Dict[int, str]:
        pass

    def list_available_resolutions(self, device_id: int) -> Optional[Tuple[Tuple[int, int], int]]:
        pass
