#  Copyright (c) 2023 actfint
#  Licensed under the BSD 3-Clause License
#  Created by @Wh1isper 2023/1/4

import asyncio
import json
from uuid import uuid4

import pytest
import y_py as Y
from jupyter_ydoc import YFile, YNotebook
from starlette.concurrency import run_in_threadpool
from starlette.testclient import WebSocketTestSession
from ypy_websocket import WebsocketProvider


async def assert_file_content(file_path, content):
    for _ in range(5):
        await asyncio.sleep(1)
        with open(file_path, "r") as f:
            content_in_file = f.read()
            if content == content_in_file:
                return
    raise TimeoutError(
        f"Timeout waiting for content == content_in_file, content:{content}, content_in_file:{content_in_file}"
    )


async def assert_cell_content(file_path, cell_content, cell_index):
    for _ in range(5):
        await asyncio.sleep(1)
        with open(file_path, "r") as f:
            try:
                cells = json.loads(f.read())["cells"]
                cell_in_file = cells[cell_index]
            except IndexError:
                continue
            if cell_content == cell_in_file:
                return
    raise TimeoutError(
        f"Timeout waiting for cell_content == cell_in_file, cell_content:{cell_content}, cell_in_file:{cell_in_file}"
    )


class WebsocketAdaptor(object):
    def __init__(self, websocket: WebSocketTestSession):
        self._websocket = websocket

    @property
    def path(self) -> str:
        # can be e.g. the URL path
        # or a room identifier
        return "test-room"

    def __aiter__(self):
        return self

    async def __anext__(self) -> bytes:
        # async iterator for receiving messages
        # until the connection is closed
        try:
            message = await self.recv()
        except:
            raise StopAsyncIteration()
        return message

    async def send(self, message: bytes):
        # send message
        await run_in_threadpool(self._websocket.send_bytes, message)

    async def recv(self) -> bytes:
        # receive message
        return await run_in_threadpool(self._websocket.receive_bytes)


async def test_ydoc_notebook(client, ipynb_file):
    path, file_path = ipynb_file
    cell = {
        "cell_type": "code",
        "execution_count": None,
        "id": str(uuid4()),
        "metadata": {},
        "outputs": [],
        "source": "",
    }

    with client.websocket_connect(f"/rtc/{path}") as websocket:
        ydoc = Y.YDoc()
        ynb = YNotebook(ydoc)
        WebsocketProvider(ydoc, WebsocketAdaptor(websocket))
        # wait for load
        await asyncio.sleep(1)
        with ydoc.begin_transaction() as t:
            ynb.append_cell(cell, t)
            cell_index = len(ynb.get()["cells"]) - 1
        # transaction finished, check update
        await assert_cell_content(file_path, cell, cell_index)


async def test_ydoc_text(client, text_file):
    path, file_path = text_file
    content = "this is a test content"

    with client.websocket_connect(f"/rtc/{path}") as websocket:
        ydoc = Y.YDoc()
        ytext = YFile(ydoc)
        WebsocketProvider(ydoc, WebsocketAdaptor(websocket))
        # wait for load
        await asyncio.sleep(0.1)
        ytext.set(content)
        await assert_file_content(file_path, content)


if __name__ == "__main__":
    pytest.main()
