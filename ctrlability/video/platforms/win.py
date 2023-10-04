from typing import Optional, Tuple, Dict

import ctrlability.video.platforms.base as base


class WindowsVideoPlatform(base.VideoPlatform):
    def get_video_format(self):
        return "dshow"

    def list_video_devices(self) -> Dict[int, str]:
        pass

    def list_available_resolutions(self, device_id: int) -> Optional[Tuple[Tuple[int, int], int]]:
        pass
