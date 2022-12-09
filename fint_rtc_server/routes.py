from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fps.hooks import register_router

from .auth import User, current_user, websocket_auth
from .base.multiuser import MultiuserManager as UserManager
from .base.session import SessionManager
from .base.ystore import YStoreManager
from .multiuser import get_user_manager
from .session import get_session_manager
from .ystore import get_ystore_manager

r = APIRouter()


@r.websocket("/api/yjs/{path}")
async def mapped_yjs_endpoint(
    path,
    user: User = Depends(current_user()),
    user_manager: UserManager = Depends(get_user_manager()),
    ystore_manager: YStoreManager = Depends(get_ystore_manager()),
    session_manager: SessionManager = Depends(get_session_manager()),
    websocket_permissions=Depends(websocket_auth(permissions={"yjs": ["read", "write"]})),
):
    if websocket_permissions is None:
        return
    websocket, permissions = websocket_permissions
    user_file_path = await user_manager.get_user_file_path(user, path)
    if not Path(user_file_path).exists():
        raise HTTPException(404, "file not found")
    ystore = await ystore_manager.get_ystore(user_file_path)
    await websocket.accept()
    async with session_manager.start_session(
        websocket, permissions, user_file_path, ystore
    ) as socket:
        await socket.serve()


router = register_router(r)
