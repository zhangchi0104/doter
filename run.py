from fire import Fire
from doter.app import DoterApp
from rich import print
import asyncio

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    print(hex(id(loop)))
    asyncio.set_event_loop(loop)
    try:
        Fire(DoterApp)
    except KeyboardInterrupt:
        app = DoterApp._get_instance()
        app._stop()
        print(":cross_mark: Task cancelled")
        exit(1)
