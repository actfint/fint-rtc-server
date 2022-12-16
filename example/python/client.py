import asyncio

import y_py as Y
from jupyter_ydoc import YFile, YNotebook
from websockets import connect
from ypy_websocket import WebsocketProvider


async def get_ipynb():
    ydoc = Y.YDoc()
    ynb = YNotebook(ydoc)
    path = "empty.ipynb"
    # asyncio.create_task(wt())
    async with connect(f"ws://localhost:8080/rtc/{path}") as websocket:
        WebsocketProvider(ydoc, websocket)
        await asyncio.sleep(1)
        print(ynb.get())
    await asyncio.sleep(0.1)  # ensure close


async def get_text():
    ydoc = Y.YDoc()
    yf = YFile(ydoc)
    path = "hello.txt"
    # asyncio.create_task(wt())
    async with connect(f"ws://localhost:8080/rtc/{path}") as websocket:
        WebsocketProvider(ydoc, websocket)
        await asyncio.sleep(1)
        print(yf.get())
    await asyncio.sleep(0.1)  # ensure close


asyncio.run(get_ipynb())
asyncio.run(get_text())
