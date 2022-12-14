#  Copyright (c) 2023 actfint
#  Licensed under the BSD 3-Clause License
#  Created by @Wh1isper 2023/1/4

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from ypy_websocket.ystore import BaseYStore, YDocNotFound
from ypy_websocket.yutils import YMessageType

from fint_rtc_server.base.websocket_handler import (
    DocRoom,
    WebsocketHandler,
    YRoomMappedWebsocketServer,
)
from fint_rtc_server.contents.utils import read_content, write_content
from fint_rtc_server.logger import logger
from fint_rtc_server.session.websocket.adapter import WebsocketAdapter
from fint_rtc_server.session.websocket.utils import FintYMessageType
from fint_rtc_server.ydoc import ydocs as YDOCS
from fint_rtc_server.ystore.manager import ManagedFileYStore

YFILE = YDOCS["file"]


def to_datetime(iso_date: str) -> datetime:
    return datetime.fromisoformat(iso_date.rstrip("Z"))


class YStoredRoom(DocRoom):
    def __init__(self, ystore: BaseYStore, is_nb_ydoc=False):
        super(YStoredRoom, self).__init__(ready=False, ystore=ystore)
        self.cleaner = None
        document_type = "notebook" if is_nb_ydoc else "file"
        self.document = YDOCS[document_type](self.ydoc)
        self.last_modified: Optional[datetime] = None


class FileMappedWebsocketServer(YRoomMappedWebsocketServer):
    rooms: Dict[str, YStoredRoom]

    def get_room(self, ystore: ManagedFileYStore) -> YStoredRoom:
        file_path = ystore.file_path
        name = str(Path(file_path).stat().st_ino)
        logger.debug(f"get room: {name}")
        return self.rooms.setdefault(name, YStoredRoom(ystore, is_notebook(Path(file_path))))


def as_json(path: Path or str) -> bool:
    if isinstance(path, str):
        path = Path(path)
    return is_notebook(path) or path.suffix == ".json"


def is_notebook(path: Path or str) -> bool:
    if isinstance(path, str):
        path = Path(path)
    return path.suffix == ".ipynb"


class YDocWebsocketHandler(WebsocketHandler):
    saving_document: Optional[asyncio.Task]
    clean_up_wait_for: int
    websocket_server = FileMappedWebsocketServer(rooms_ready=False, auto_clean_rooms=False)

    def __init__(
        self,
        websocket: WebsocketAdapter,
        ystore,
        user,
        clean_up_wait_for=60,
        save_wait_for=1,
    ):
        super().__init__(websocket, ystore, user)
        self.clean_up_wait_for = clean_up_wait_for
        self.save_wait_for = save_wait_for

    @property
    def path(self):
        return self.websocket.file_path

    @property
    def last_modified(self):
        return self.room.last_modified

    @last_modified.setter
    def last_modified(self, value: Optional[datetime]):
        self.room.last_modified = value

    async def serve(self):
        self.saving_document = None
        self.room.on_message = self.on_message

        if self.room.cleaner is not None:
            logger.debug(f"Reconnect room {self.room}, cancel cleaner")
            self.room.cleaner.cancel()

        if not self.room.ready:
            file_path = Path(self.path)
            model = await read_content(file_path, get_content=True, as_json=as_json(file_path))
            self.last_modified = to_datetime(model.last_modified)

            # double check, await before
            if not self.room.ready:
                try:
                    await self.room.ystore.apply_updates(self.room.ydoc)
                except YDocNotFound:
                    # YDoc not found in the YStore, create the document from
                    # the source file (no change history)
                    await self.update_from_source(model)
                if self.room.document.source != model.content:
                    await self.update_from_source(model)
                self.room.document.dirty = False
                self.room.ready = True
                # save the document when changed
                self.room.document.observe(self.on_document_change)

        await self.websocket_server.serve(self.websocket)
        await self.on_close()

    async def send_event_msg(self, msg: bytes):
        msg = bytes([FintYMessageType.EVENT]) + msg
        await self.websocket.send(msg)

    async def on_close(self):
        async def cleanup():
            await asyncio.sleep(self.clean_up_wait_for)
            if self.saving_document:
                # ensure file change saved
                await self.saving_document
            self.room.document.unobserve()
            self.websocket_server.delete_room(room=self.room)
            logger.info(f"room: {self.room} has been cleaned")

        logger.debug(f"Current clients in room {self.room}: {self.room.clients}")
        if not self.room.clients:
            logger.info("no clients left, schedule cleanup task...")
            self.room.cleaner = asyncio.create_task(cleanup())

    def on_document_change(self, event):
        try:
            dirty = event.keys["dirty"]["newValue"]
            if not dirty:
                # we cleared the dirty flag, nothing to save
                return
        except Exception:
            pass
        # unobserve and observe again because the structure of the document may have changed
        # e.g. a new cell added to a notebook
        self.room.document.unobserve()
        self.room.document.observe(self.on_document_change)
        if self.saving_document is not None and not self.saving_document.done():
            # the document is being saved, cancel that
            self.saving_document.cancel()
            self.saving_document = None
        self.saving_document = asyncio.create_task(self.maybe_save_document())

    async def maybe_save_document(self):
        # save after save_wait_for second of inactivity to prevent too frequent saving
        await asyncio.sleep(self.save_wait_for)
        logger.info(f"try save {self.path}")
        file_path = Path(self.path)
        model = await read_content(file_path, True, as_json=as_json(file_path))
        if self.last_modified < to_datetime(model.last_modified):
            # file changed on disk, let's revert
            logger.info(
                f"file {self.path} changed on disk, will not save file but load file(save next time)"
            )
            self.room.document.source = model.content
            self.last_modified = to_datetime(model.last_modified)
            return
        if model.content != self.room.document.source:
            # don't save if not needed
            # this also prevents the dirty flag from bouncing between windows of
            # the same document opened as different types (e.g. notebook/text editor)
            if is_notebook(file_path):
                file_type = "notebook"
            else:
                file_type = "json" if as_json(file_path) else "text"
            file_format = "json" if as_json(file_path) else "text"
            content = {
                "content": self.room.document.source,
                "format": file_format,
                "path": file_path.as_posix(),
                "type": file_type,
            }
            await write_content(content)
            logger.info(f"{self.path} saved")
            model = await read_content(file_path, False)
            self.last_modified = to_datetime(model.last_modified)
        self.room.document.dirty = False

    async def update_from_source(self, model):
        self.room.document.source = model.content
        await self.room.ystore.encode_state_as_update(self.room.ydoc)

    async def on_message(self, message: bytes) -> bool:
        """
        Called whenever a message is received, before forwarding it to other clients.

        :param: message: received message
        :returns: True if the message must be discarded, False otherwise (default: False).
        """
        skip = False
        byte = message[0]
        msg = message[1:]
        if byte == YMessageType.SYNC:
            if not self.can_write and msg[0] == YMessageType.SYNC_UPDATE:
                skip = True
        elif byte == YMessageType.AWARENESS or FintYMessageType.EVENT:
            # AWARENESS should broadcast to all client
            pass
        else:
            skip = True

        return skip

    async def maybe_load_document(self):
        file_path = Path(self.path)
        model = await read_content(file_path, False)
        # do nothing if the file was saved by us
        if self.last_modified < to_datetime(model.last_modified):
            logger.debug(f"Reload document: {file_path}")
            model = await read_content(file_path, get_content=True, as_json=as_json(file_path))
            self.room.document.source = model.content
            self.last_modified = to_datetime(model.last_modified)
