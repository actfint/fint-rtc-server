from ypy_websocket.ystore import BaseYStore


class YStoreManager(object):
    async def get_ystore(self, path) -> BaseYStore:
        raise NotImplementedError
