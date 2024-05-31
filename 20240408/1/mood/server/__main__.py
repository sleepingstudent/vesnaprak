"""Server runner."""

from .server import main, Area, swap_monster_foo
import asyncio
import threading


area = Area()
monster_swap_thr = threading.Thread(target=swap_monster_foo, args=(area, ))
monster_swap_thr.start()
asyncio.run(main(area))
