/*
 * Copyright (c) 2023 actfint
 * Licensed under the BSD 3-Clause License
 * Created by @Wh1isper 2023/1/4
 */

import { YNotebook } from '@jupyter/ydoc'
import { WebsocketProvider } from 'y-websocket'

const notebook = new YNotebook()
import ws from 'ws'

const wsProvider = new WebsocketProvider(
    'ws://localhost:8080/rtc', 'empty.ipynb',
    notebook.ydoc,
    {WebSocketPolyfill: ws}
)

wsProvider.on('status', event => {
    console.log(event.status)
})

notebook.ydoc.on('update', on_change)

function on_change(update) {
    try {
        console.log(notebook.toJSON())
    }catch(err){
    }
}
