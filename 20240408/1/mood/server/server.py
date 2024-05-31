"""Server for MUD."""

from cowsay import cowsay, list_cows, read_dot_cow
from io import StringIO
import shlex
import asyncio
import time
import random


clients: dict[str, asyncio.Queue] = {}


async def run_swap(area, vr_x, vr_y, move):
    """run_swap. 
    main for asyncio.run() in swap_monster_foo

    :param area: area for game
    :param vr_x: x pos for monster
    :param vr_y: y pos for monster
    :param move: move type (right, left, up, down)
    """
    await area.monster_permut(vr_x, vr_y, move)


def swap_monster_foo(area):
    """swap_monster_foo.
    swap foo in new thread

    :param area: area for game
    """
    start_time = time.time()

    pos_to_name = {(1, 0) : 'right', (-1, 0) : 'left', (0, 1) : 'up', (0, -1) : 'down'}

    while True:
        if (time.time() - start_time) >= 30.0:
            monster_pos = []

            for i, monster in enumerate(area.monster):
                for j, monster_i in enumerate(monster):
                    if monster_i is not None:
                        monster_pos.append([i, j])

            if len(monster_pos) == 0:
                start_time = time.time()
                continue

            while True:
                sw_i, sw_j = monster_pos[random.randrange(len(monster_pos))]

                move = list(pos_to_name.keys())[random.randrange(4)]

                vr_x, vr_y = area.monster[sw_i][sw_j].x,  area.monster[sw_i][sw_j].y

                vr_x += move[0]
                vr_y += move[1]
                
                if vr_x == -1:
                    vr_x = 9
                elif vr_x == 10:
                    vr_x = 0

                if vr_y == -1:
                    vr_y = 9
                elif vr_y == 10:
                    vr_y = 0

                if area.monster[vr_x][vr_y] is not None:
                    continue

                area.monster[vr_x][vr_y] = area.monster[sw_i][sw_j]
                area.monster[sw_i][sw_j] = None

                asyncio.run(run_swap(area, vr_x, vr_y, pos_to_name[move]))
                break

            start_time = time.time()


class MonsterConst():
    """MonsterConst."""

    def __init__(self):
        """__init__."""
        self.cow = read_dot_cow(StringIO("""
        $the_cow = <<EOC;
            ,_                    _,
            ) '-._  ,_    _,  _.-' (
            )  _.-'.|\\\0\\--//|.'-._  (
             )'   .'\\/o\\/o\\/'.   `(
              ) .' . \\====/ . '. (
               )  / <<    >> \\  (
                '-._/``  ``\\_.-'
          jgs     __\\\0\\'--'//__
                 (((""`  `"")))
        EOC
        """))


class Monster():
    """Monster."""

    def __init__(self, x, y, hi, name, hp):
        """__init__.

        :param x: x pos
        :param y: y pos 
        :param hi: what say
        :param name: name of monster
        :param hp: hitpoints 
        """
        self.x = x
        self.y = y
        self.text = hi
        self.name = name
        self.jgsbat = MonsterConst().cow
        self.hp = hp

    def __str__(self):
        """__str__."""
        if self.name == "jgsbat":
            return cowsay(self.text, cowfile=self.jgsbat)
        else:
            return cowsay(self.text, cow=self.name)


class Pers():
    """Pers."""

    def __init__(self, name, x=0, y=0):
        """__init__.

        :param name: name client
        :param x: x pos
        :param y: y pos
        """
        self.x = x
        self.y = y
        self.name = name

    def move_x(self, step):
        """move_x.

        :param step: step for x
        """
        self.x += step

        if self.x == -1:
            self.x = 9
        elif self.x == 10:
            self.x = 0

    def move_y(self, step):
        """move_y.

        :param step: step for y
        """
        self.y -= step

        if self.y == -1:
            self.y = 9
        elif self.y == 10:
            self.y = 0


class Area():
    """Area."""

    def __init__(self):
        """__init__."""
        self.pers: dict[str, Pers] = {}
        self.monster = [[None for j in range(10)] for i in range(10)]

        self.weapon = {'sword': 10, 'spear': 15, 'axe': 20}

    async def moved_to(self, x, y, client_name):
        """moved_to.

        :param x: x step
        :param y: t step
        :param client_name: name of client
        """
        self.pers[client_name].move_x(x)
        self.pers[client_name].move_y(y)

        add_str = f'Moved to ({self.pers[client_name].x}, {self.pers[client_name].y})'

        await self.encounter(self.pers[client_name].x, self.pers[client_name].y, client_name, add_str)

    async def addmon(self, x, y, hi, name, hp, client_name):
        """addmon.

        :param x: x pos
        :param y: y pos
        :param hi: what say
        :param name: name of monster
        :param hp: hitpoints
        :param client_name: who add monster
        """
        if name not in list_cows() and name != 'jgsbat':
            await clients[client_name].put('Cannot add unknown monster')
            return

        vr_monster = self.monster[x][y]

        self.monster[x][y] = Monster(x, y, hi, name, hp)

        add_str = f'Added monster {name} to ({x}, {y}) saying {hi}'

        if vr_monster is not None:
            await clients[client_name].put(f'{add_str}\nReplaced the old monster')
        else:
            await clients[client_name].put(add_str)

        for out in clients.values():
            if out is not clients[client_name]:
                await out.put(f'The {client_name} added monster {name} with {hp} hp')

    async def encounter(self, x, y, client_name, add_str):
        """encounter.

        :param x: x pos for client
        :param y: y pos for client
        :param client_name: client name
        :param add_str: prev str
        """
        if add_str != '':
            if self.monster[x][y] is not None:
                await clients[client_name].put(f'{add_str}\n{self.monster[x][y].__str__()}')
            else:
                await clients[client_name].put(add_str)
        else:
            if self.monster[x][y] is not None:
                await clients[client_name].put(f'{self.monster[x][y].__str__()}')

    async def attack(self, monster_name, weapon, client_name):
        """attack.

        :param monster_name: name monster
        :param weapon: weapon type
        :param client_name: client name
        """
        if self.monster[self.pers[client_name].x][self.pers[client_name].y] is None:
            await clients[client_name].put('No monster here')
        else:
            damag = self.weapon[weapon]

            vr_hp = self.monster[self.pers[client_name].x][self.pers[client_name].y].hp
            vr_name = self.monster[self.pers[client_name].x][self.pers[client_name].y].name

            if monster_name != vr_name:
                await clients[client_name].put(f'No {monster_name} here')
                return

            if vr_hp > damag:
                self.monster[self.pers[client_name].x][self.pers[client_name].y].hp -= damag
                vr_hp = damag
            else:
                self.monster[self.pers[client_name].x][self.pers[client_name].y] = None

            add_str_main = f'Attacked {vr_name}, damage {vr_hp} hp'

            if self.monster[self.pers[client_name].x][self.pers[client_name].y] is None:
                add_str = f'{vr_name} died'
            else:
                add_str = f'{vr_name} now has {self.monster[self.pers[client_name].x][self.pers[client_name].y].hp}'

            await clients[client_name].put(f'{add_str_main}\n{add_str}')

            for out in clients.values():
                if out is not clients[client_name]:
                    await out.put(f'The {client_name} attacked the {vr_name} at ({self.pers[client_name].x}, '\
                                  f'{self.pers[client_name].y}) with {weapon}, damage {vr_hp} hp, {add_str}')

    async def monster_permut(self, i, j, move_n):
        """monster_permut.

        :param i: x pos 
        :param j: y pos
        :param move_n: move type
        """
        for out in clients.values():
            await out.put(f'{self.monster[i][j].name} moved one cell {move_n}')

        for client_str, client in self.pers.items():
            if client.x == i and client.y == j:
                await self.encounter(client.x, client.y, client_str, '')


async def game(reader, writer, area):
    """game.

    :param reader: reader
    :param writer: writer
    :param area: area for game
    """
    log = await reader.readline()

    client_name = log.decode().strip()

    if client_name in clients.keys():
        writer.write(b'no')

        await writer.drain()

        await reader.readline()

        writer.close()
        await writer.wait_closed()

        return
    else:
        writer.write(b'yes')

        await writer.drain()

    clients[client_name] = asyncio.Queue()

    area.pers[client_name] = Pers(client_name)

    for out in clients.values():
        if out is not clients[client_name]:
            await out.put(f'The {client_name} has joined the game')

    send = asyncio.create_task(reader.readline())
    receive = asyncio.create_task(clients[client_name].get())

    while not reader.at_eof():
        done, pending = await asyncio.wait([send, receive], timeout=1, return_when=asyncio.FIRST_COMPLETED)

        for q in done:
            if q is send:
                data = q.result().decode().strip()

                s = shlex.split(data)

                match s:
                    case ['move', x, y]:
                        await area.moved_to(int(x), int(y), client_name)
                    case ['addmon', x, y, hello_string, monster_name, hp]:
                        await area.addmon(int(x), int(y), hello_string, monster_name, int(hp), client_name)
                    case ['attack', monster_name, 'with', weapon]:
                        await area.attack(monster_name, weapon, client_name)
                    case ['sayall', args]:
                        for out in clients.values():
                            if out is not clients[client_name]:
                                await out.put(f'{client_name}: {args}')

                send = asyncio.create_task(reader.readline())
            else:
                writer.write(f'{q.result()}'.encode())
                await writer.drain()

                receive = asyncio.create_task(clients[client_name].get())

    for out in clients.values():
        if out is not clients[client_name]:
            await out.put(f'The {client_name} left the game')

    del area.pers[client_name]
    del clients[client_name]

    writer.close()
    await writer.wait_closed()


async def main(area):
    """main.

    :param area: area for game
    """
    server = await asyncio.start_server(lambda r, w: game(r, w, area), '0.0.0.0', 1337)
    async with server:
        await server.serve_forever()
