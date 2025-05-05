import asyncio, sys
from server.main import main as server_main

def main():
    try:
        asyncio.run(server_main())
    except KeyboardInterrupt:
        print("\n[server] stopped", file=sys.stderr)
