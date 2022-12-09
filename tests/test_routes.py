import asyncio
import json
from uuid import uuid4

import pytest
import y_py as Y
from jupyter_ydoc import YFile, YNotebook
from starlette.concurrency import run_in_threadpool
from starlette.testclient import WebSocketTestSession
from ypy_websocket import WebsocketProvider


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

    with client.websocket_connect(f"/api/yjs/{path}") as websocket:
        ydoc = Y.YDoc()
        ynb = YNotebook(ydoc)
        WebsocketProvider(ydoc, WebsocketAdaptor(websocket))
        # wait for load
        await asyncio.sleep(0.1)
        with ydoc.begin_transaction() as t:
            ynb.append_cell(cell, t)
        # wait for file saved
        # fixme using pool instead of sleep
        await asyncio.sleep(2)

    with open(file_path, "r") as f:
        cell_in_file = json.loads(f.read())["cells"][1]
        assert cell == cell_in_file


async def test_ydoc_text(client, text_file):
    path, file_path = text_file
    content = "this is a test content"

    with client.websocket_connect(f"/api/yjs/{path}") as websocket:
        ydoc = Y.YDoc()
        ytext = YFile(ydoc)
        WebsocketProvider(ydoc, WebsocketAdaptor(websocket))
        # wait for load
        await asyncio.sleep(0.1)
        ytext.set(content)
        # wait for file saved
        # fixme using pool instead of sleep
        await asyncio.sleep(2)

    with open(file_path, "r") as f:
        content_in_file = f.read()
        assert content == content_in_file


if __name__ == "__main__":
    pytest.main()
