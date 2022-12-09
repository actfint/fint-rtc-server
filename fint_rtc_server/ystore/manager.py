from datetime import datetime
from pathlib import Path

from fastapi import Depends
from ypy_websocket.ystore import FileYStore

from fint_rtc_server.base.singleton import Singleton
from fint_rtc_server.base.ystore import YStoreManager
from fint_rtc_server.config import FintRTCServerConfig, get_config
from fint_rtc_server.logger import logger


def get_ystore_manager():
    def _(
        server_config: FintRTCServerConfig = Depends(get_config),
    ):
        return INOMappedYStoreManager(server_config.room_dir)

    return _


async def metadata_callback() -> bytes:
    return datetime.utcnow().isoformat().encode()


class ManagedFileYStore(FileYStore):
    def __init__(self, file_path: str, path: str, metadata_callback=None):
        super().__init__(path, metadata_callback)
        self.file_path = file_path


class INOMappedYStoreManager(YStoreManager, metaclass=Singleton):
    """
    Single disk, unique room determined by ino
    """

    def __init__(self, room_dir):
        self.room_dir = room_dir

    async def get_ystore(self, path: Path) -> ManagedFileYStore:
        y_path = self.ystore_path(path)
        self.init_local_ystore(y_path)
        return ManagedFileYStore(path.as_posix(), y_path.as_posix(), metadata_callback)

    def ystore_path(self, path: Path):
        return Path(self.room_dir) / path.as_posix().lstrip("/") / str(path.stat().st_ino)

    def init_local_ystore(self, y_path: Path):
        y_path.parent.mkdir(parents=True, exist_ok=True)
        self.clean_old_ystore(y_path)

    def clean_old_ystore(self, y_path: Path):

        for ystore_file in y_path.parent.glob("*"):
            if y_path.exists() and ystore_file.samefile(y_path):
                continue
            logger.info(f"Remove old ystore {ystore_file}")
            ystore_file.unlink()
