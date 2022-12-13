import os
from typing import Optional

from fps.config import PluginModel
from fps.config import get_config as fps_get_config
from fps.hooks import register_config, register_plugin_name


class FintRTCServerConfig(PluginModel):
    content_dir: Optional[str] = os.getenv("FINT_RTC_CONTENT_DIR", "/var/fint/rtc-server/")
    room_dir: Optional[str] = os.getenv("FINT_RTC_ROOM_DIR", "/var/fint/rtc-room")
    room_cleanup_wait_for: Optional[int] = 60
    doc_save_wait_for: Optional[float] = 1.0


def get_config():
    return fps_get_config(FintRTCServerConfig)


c = register_config(FintRTCServerConfig)
n = register_plugin_name("fint-rtc-server")
