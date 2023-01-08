#  Copyright (c) 2023 actfint
#  Licensed under the BSD 3-Clause License
#  Created by @Wh1isper 2023/1/4

import asyncio
import contextlib
import json
from pathlib import Path
from typing import Dict, List, Type

from fastapi import Depends, WebSocket
from watchfiles import Change, awatch

from fint_rtc_server.base.session import SessionManager as BaseSessionManager
from fint_rtc_server.base.singleton import Singleton
from fint_rtc_server.config import FintRTCServerConfig, get_config
from fint_rtc_server.logger import logger
from fint_rtc_server.session.websocket.adapter import WebsocketAdapter
from fint_rtc_server.session.websocket.handler import YDocWebsocketHandler
from fint_rtc_server.ystore.manager import ManagedFileYStore

_manager = None


def get_session_manager(
    server_config: FintRTCServerConfig = Depends(get_config),
):
    return WebSocketSessionManager(
        YDocWebsocketHandler,
        server_config.room_cleanup_wait_for,
        server_config.doc_save_wait_for,
    )


class WebSocketSessionManager(BaseSessionManager, metaclass=Singleton):
    session: Dict[str, List[YDocWebsocketHandler]] = dict()
    watcher: Dict[str, asyncio.Task] = dict()
    handler_cls: Type[YDocWebsocketHandler]

    def __init__(self, handler_cls, room_cleanup_wait_for, doc_save_wait_for):
        super(WebSocketSessionManager, self).__init__(handler_cls)
        self.room_cleanup_wait_for = room_cleanup_wait_for
        self.doc_save_wait_for = doc_save_wait_for

    @contextlib.asynccontextmanager
    async def start_session(
        self, websocket: WebSocket, user, file_path: str, ystore: ManagedFileYStore
    ):
        if isinstance(file_path, Path):
            file_path = file_path.as_posix()
        socket = self.handler_cls(
            WebsocketAdapter(websocket, ystore, file_path),
            ystore,
            user,
            self.room_cleanup_wait_for,
            self.doc_save_wait_for,
        )
        await self.prepare(file_path, socket)

        try:
            yield socket
        except Exception as e:
            logger.exception(e)
        finally:
            await self.close_session(file_path, socket)

    async def close_session(self, file_path, websocket: YDocWebsocketHandler, *args, **kwargs):
        self.session[file_path].remove(websocket)
        if not self.session[file_path]:
            logger.info(f"Session closed, cancel watch file: {file_path}")
            self.watcher[file_path].cancel()
            del self.watcher[file_path]

        try:
            await websocket.close()
        except RuntimeError:
            pass

    async def close_all_session(self, file_path, reason=""):
        for websocket in self.session[file_path]:
            msg = json.dumps(["disconnect", reason]).encode("utf-8")
            await websocket.send_event_msg(msg)
            await websocket.close()

    async def prepare(self, file_path, websocket: YDocWebsocketHandler):
        self.session.setdefault(file_path, []).append(websocket)
        self._add_watcher(file_path)

    def _add_watcher(self, file_path, recreate=False):
        if recreate:
            old_task = None
            if file_path in self.watcher:
                old_task = self.watcher[file_path]
            self.watcher[file_path] = asyncio.create_task(self.watch_file_exist(file_path))
            if old_task:
                old_task.cancel()
        else:
            if file_path not in self.watcher:
                self.watcher[file_path] = asyncio.create_task(self.watch_file_exist(file_path))

    async def watch_file_exist(self, file_path):
        p = Path(file_path)
        logger.info(f"start watch file: {file_path}")
        if not p.exists():
            logger.info(f"{p} has been deleted, close all session")
            return await self.close_all_session(file_path, "File deleted")
        try:
            async for changes in awatch(p):
                for change, _ in changes:
                    if change == Change.deleted:
                        logger.info(f"{p} has been deleted, close all session")
                        return await self.close_all_session(file_path, "File deleted")
                    await self.notify_update(file_path)
        except RuntimeError as e:
            logger.exception(e)
            if not p.exists():
                logger.info(f"{p} has been deleted, close all session")
                return await self.close_all_session(file_path, "File deleted")
        except Exception as e:
            # rewatch
            logger.exception(e)
            return self._add_watcher(file_path, recreate=True)

    async def notify_update(self, file_path):
        # Only need load one of session, room will broadcast
        websocket = self.session[file_path][0]
        if websocket.room.ready:
            await websocket.maybe_load_document()
