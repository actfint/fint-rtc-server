from typing import Dict

from ypy_websocket import WebsocketServer
from ypy_websocket.websocket_server import YRoom
from ypy_websocket.ystore import BaseYStore

from fint_rtc_server.ydoc import YFile, YNotebook


class DocRoom(YRoom):
    document: YFile or YNotebook


class YRoomMappedWebsocketServer(WebsocketServer):
    rooms: Dict[str, DocRoom]

    def get_room(self, ystore: BaseYStore) -> DocRoom:
        raise NotImplementedError


class WebsocketHandler:
    websocket_server: YRoomMappedWebsocketServer

    def __init__(self, websocket, ystore, permissions):
        self.websocket = websocket
        self.can_write = permissions is None or "write" in permissions.get("yjs", [])
        self.room = self.websocket_server.get_room(ystore)

    async def serve(self):
        raise NotImplementedError

    async def close(self):
        await self.websocket.close()
