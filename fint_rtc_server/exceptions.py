from typing import Any, Dict, Optional

from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
from fps.hooks import register_exception_handler

from .logger import logger


class ServerException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, Any]] = None,
        response_detail: Any = "Exception response detail not defined",
        content: Any = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.response_detail = response_detail
        self.content = content


async def server_exception_handler(request: Request, exc: ServerException) -> Response:
    logger.exception(exc)
    logger.error(f"Exception ( {exc.detail} ) occurred, response with {exc.status_code}")
    if not exc.content:
        response = JSONResponse(
            content={"detail": f"{exc.response_detail}"},
            status_code=exc.status_code,
            headers=exc.headers,
        )
    else:
        response = JSONResponse(
            content=exc.content,
            status_code=exc.status_code,
            headers=exc.headers,
        )

    return response


async def default_exception_handler(request: Request, exc: HTTPException) -> Response:
    logger.exception(exc)
    logger.error(f"Exception ( {exc.detail} ) occurred, response with {exc.status_code}")
    return JSONResponse(
        content={"detail": f"{exc.detail}"}, status_code=exc.status_code, headers=exc.headers
    )


h_server = register_exception_handler(ServerException, server_exception_handler)
h_default = register_exception_handler(HTTPException, default_exception_handler)
