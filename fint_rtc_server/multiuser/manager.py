#  Copyright (c) 2023 actfint
#  Licensed under the BSD 3-Clause License
#  Created by @Wh1isper 2023/1/4

from pathlib import Path

from fastapi import Depends

from fint_rtc_server.auth import User
from fint_rtc_server.base.multiuser import MultiuserManager
from fint_rtc_server.base.singleton import Singleton
from fint_rtc_server.config import FintRTCServerConfig, get_config


def get_user_manager(
    server_config: FintRTCServerConfig = Depends(get_config),
):
    return UidMappedUserManager(server_config.content_dir)


class UidMappedUserManager(MultiuserManager, metaclass=Singleton):
    def __init__(self, root_dir):
        self.root_dir = root_dir

    async def get_user_file_path(self, user: User, path, *args, **kwargs) -> Path:
        p = Path(self.root_dir) / user.user_id / path
        return p
