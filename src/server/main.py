import asyncio, json, signal, time, websockets
from contextlib import suppress
from pvninja.events import ServerTick, ButtonCommand

HOST, PORT = "0.0.0.0", 8765
clients: set[websockets.WebSocketServerProtocol] = set()
start_time = time.perf_counter()

async def handle(ws):
    clients.add(ws)
    try:
        async for raw in ws:
            cmd = ButtonCommand.model_validate_json(raw)
            print(f"[SERVER] got command: {cmd.action}")
    finally:
        clients.discard(ws)

async def broadcaster():
    while True:
        await asyncio.sleep(1)
        msg = ServerTick(value=int(time.perf_counter() - start_time))
        for ws in clients.copy():
            with suppress(Exception):
                await ws.send(msg.model_dump_json())

async def main():
    async with websockets.serve(handle, HOST, PORT):
        print(f"Server listening on ws://{HOST}:{PORT}")
        await broadcaster()           # never returns

if __name__ == "__main__":
    # graceful CTRL‑C
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: asyncio.get_event_loop().stop())
    asyncio.run(main())
