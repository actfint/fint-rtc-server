#  Copyright (c) 2023 actfint
#  Licensed under the BSD 3-Clause License
#  Created by @Wh1isper 2023/1/4

from ypy_websocket.ystore import BaseYStore


class YStoreManager(object):
    async def get_ystore(self, path) -> BaseYStore:
        raise NotImplementedError
