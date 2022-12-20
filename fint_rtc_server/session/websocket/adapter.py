# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.


from fastapi import WebSocket, WebSocketDisconnect

from fint_rtc_server.logger import logger


class WebsocketAdapter:
    """An adapter to make a Starlette's WebSocket look like a ypy-websocket's WebSocket"""

    def __init__(self, websocket: WebSocket, path, file_path):
        self._websocket = websocket
        self._path = path
        self.file_path = file_path

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, value: str) -> None:
        self._path = value

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            message = await self._websocket.receive_bytes()
        except WebSocketDisconnect:
            raise StopAsyncIteration()
        return message

    async def send(self, message):
        try:
            await self._websocket.send_bytes(message)
        except RuntimeError as e:
            logger.exception(e)
            await self.close()

    async def recv(self):
        return await self._websocket.receive_bytes()

    async def close(self):
        return await self._websocket.close()
