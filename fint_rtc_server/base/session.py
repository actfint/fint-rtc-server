import contextlib
from typing import Type

from fint_rtc_server.base.websocket_handler import WebsocketHandler


class SessionManager(object):
    handler_cls: Type[WebsocketHandler]

    def __init__(self, handler_cls: Type[WebsocketHandler]):
        self.handler_cls = handler_cls

    @contextlib.asynccontextmanager
    async def start_session(self, websocket, permissions, file_path, ystore):
        raise NotImplementedError

    async def close_session(self, *args, **kwargs):
        raise NotImplementedError

    async def prepare(self, *args, **kwargs):
        # run before websocket handler serve
        pass
