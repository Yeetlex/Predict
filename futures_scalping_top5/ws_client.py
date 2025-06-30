# ws_client.py

import asyncio
import websockets
import json
import threading
import time
from rest_api import add_tick_to_buffer
from config import TOP_SYMBOLS, WS_RECONNECT_INTERVAL, DEBUG

class BinanceWSClient:
    def __init__(self, reconnect_interval=WS_RECONNECT_INTERVAL):
        self.reconnect_interval = reconnect_interval
        self.running = True
        self.symbols = [s.lower() for s in TOP_SYMBOLS]

    def _build_stream_url(self):
        streams = [f"{sym}@trade" for sym in self.symbols]
        return f"wss://fstream.binance.com/stream?streams={'/'.join(streams)}"

    async def _ws_handler(self):
        while self.running:
            try:
                url = self._build_stream_url()
                if DEBUG:
                    print(f"Connecting to Binance WS: {url}")
                
                async with websockets.connect(url, ping_interval=30, ping_timeout=10) as websocket:
                    if DEBUG:
                        print("WebSocket connection established")
                    
                    while self.running:
                        try:
                            message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                            data = json.loads(message)
                            stream = data.get('stream', '')
                            
                            if '@trade' in stream:
                                trade_data = data.get('data', {})
                                symbol = trade_data.get('s', '').upper()
                                price = float(trade_data.get('p', 0))
                                timestamp = trade_data.get('T', 0)
                                
                                if symbol.lower() in self.symbols:
                                    add_tick_to_buffer(
                                        symbol, 
                                        {'price': price, 'timestamp': timestamp}
                                    )
                        except asyncio.TimeoutError:
                            continue
                        except Exception as e:
                            if DEBUG:
                                print(f"Error processing message: {str(e)[:100]}")
            except Exception as e:
                if DEBUG:
                    print(f"WebSocket error: {str(e)[:100]} - Reconnecting in {self.reconnect_interval}s")
                await asyncio.sleep(self.reconnect_interval)

    def start(self):
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._ws_handler())

    def stop(self):
        self.running = False