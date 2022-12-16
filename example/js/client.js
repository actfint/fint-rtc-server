import { YNotebook } from '@jupyter/ydoc'
import { WebsocketProvider } from 'y-websocket'

const notebook = new YNotebook()
import ws from 'ws'

const wsProvider = new WebsocketProvider(
    'ws://hasee.v6:8080/rtc', 'empty.ipynb',
    notebook.ydoc,
    {WebSocketPolyfill: ws}
)

wsProvider.on('status', event => {
    console.log(event.status)
})

function on_change(self, change) {
    console.log(change)
    // try {
    //     console.log(self.toJSON())
    // }catch(err){
    // }
}
