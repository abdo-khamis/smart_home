from lib.init import *
import asyncio, websockets

class WSClient(QThread):
    message_received = Signal(str)
    send_message = Signal(str)

    def __init__(self):
        super().__init__()
        self.loop = None
        self.ws = None
        self.send_message.connect(self.queue_message)
        self._message_queue = asyncio.Queue()
        self.uri = "ws://192.168.4.1/SmartHomeServer"
        self._reconnect_delay = 3    

    def run(self):
        asyncio.run(self.listen_forever())

    def queue_message(self, msg):
    
        if self.loop:
            asyncio.run_coroutine_threadsafe(self._message_queue.put(msg), self.loop)

    async def listen_forever(self):
        while True:
            try:
                await self.listen()
            except Exception as e:
                print(f" Connection error: {e}")
            print(f" Reconnecting in {self._reconnect_delay} seconds...")
            await asyncio.sleep(self._reconnect_delay)

    async def listen(self):
        """الاتصال الأساسي"""
        async with websockets.connect(
            self.uri,
            ping_interval=20,        
            ping_timeout=20,   
        ) as ws:
            self.ws = ws
            self.loop = asyncio.get_running_loop()
            print(" Connected to WebSocket server")

            receiver = asyncio.create_task(self._receive_loop())
            sender = asyncio.create_task(self._send_loop())
            await asyncio.gather(receiver, sender)

    async def _receive_loop(self):
        try:
            async for msg in self.ws:
                self.message_received.emit(msg)
        except Exception as e:
            print(" Receive loop error:", e)
            raise e 

    async def _send_loop(self):
        while True:
            msg = await self._message_queue.get()
            if self.ws and self.ws.open:
                try:
                    await self.ws.send(msg)
                except Exception as e:
                    print(" Send failed:", e)

