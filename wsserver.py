import asyncio
import json
from websockets import serve


class WebSocketServer:
    connection = None
    port = 8081
    leds = 0

    def start(self):
        asyncio.run(self._start())

    async def _start(self):
        async with serve(self.onMessage, "0.0.0.0", self.port):
            print("Listening to ws://0.0.0.0:%d" % self.port)
            await asyncio.Future()  # run forever

    async def onMessage(self, websocket):
        self.connection = websocket  # Store the connection to whichever client messaged last
        async for message in websocket:
            print("Received message: %s" % message)
            if message == 'hello':
                await websocket.send(json.dumps({
                    "leds": self.leds
                }))

    def send(self, message):
        asyncio.run(self._send(message))

    async def _send(self, message):
        if self.connection:
            try:
                await self.connection.send(message)
            except Exception as e:
                print("WS send() Exception: " + str(e))
                self.connection = None
