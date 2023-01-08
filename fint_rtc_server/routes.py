#  Copyright (c) 2023 actfint
#  Licensed under the BSD 3-Clause License
#  Created by @Wh1isper 2023/1/4

from pathlib import Path

from fastapi import APIRouter, Depends
from fps.hooks import register_router

from .auth import websocket_auth
from .base.multiuser import MultiuserManager as UserManager
from .base.session import SessionManager
from .base.ystore import YStoreManager
from .exceptions import ServerException
from .logger import logger
from .multiuser import get_user_manager
from .session import get_session_manager
from .ystore import get_ystore_manager

r = APIRouter()


@r.websocket("/rtc/{path:path}")
async def mapped_yjs_endpoint(
    path,
    user_manager: UserManager = Depends(get_user_manager),
    ystore_manager: YStoreManager = Depends(get_ystore_manager),
    session_manager: SessionManager = Depends(get_session_manager),
    websocket_permissions=Depends(websocket_auth),
):
    if not websocket_permissions:
        return
    websocket, user = websocket_permissions
    user_file_path = await user_manager.get_user_file_path(user, path)
    if not Path(user_file_path).exists():
        logger.info(f"{user_file_path} not found")
        raise ServerException(404, "file not found", response_detail=f"File not found: {path}")
    ystore = await ystore_manager.get_ystore(user_file_path)
    await websocket.accept()
    async with session_manager.start_session(websocket, user, user_file_path, ystore) as socket:
        await socket.serve()


router = register_router(r)
