#  Copyright (c) 2023 actfint
#  Licensed under the BSD 3-Clause License
#  Created by @Wh1isper 2023/1/4

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

    def __init__(self, websocket, ystore, user):
        self.websocket = websocket
        # todo user may not write this file
        self.can_write = True
        self.room = self.websocket_server.get_room(ystore)

    async def serve(self):
        raise NotImplementedError

    async def close(self):
        await self.websocket.close()
