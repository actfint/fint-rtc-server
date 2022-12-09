from typing import Optional

from fps.config import PluginModel
from fps.config import get_config as fps_get_config
from fps.hooks import register_config, register_plugin_name


class FintRTCServerConfig(PluginModel):
    content_dir: Optional[str] = "/var/fint/rtc-server/"
    room_dir: Optional[str] = "/var/fint/rtc-room"
    room_cleanup_wait_for: Optional[int] = 60
    doc_save_wait_for: Optional[float] = 1.0

    remote_location: Optional[str] = ""


def get_config():
    return fps_get_config(FintRTCServerConfig)


c = register_config(FintRTCServerConfig)
n = register_plugin_name("fint-rtc-server")
