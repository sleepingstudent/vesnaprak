#!/usr/bin/env python3
import cowsay
import cmd
from io import StringIO
import sys
import socket
import shlex
import asyncio
import re

pattern = re.compile(r'\w+')


class Mud():
    jgsbat = cowsay.read_dot_cow(StringIO("""
    $the_cow = <<EOC;
        ,_                    _,
        ) '-._  ,_    _,  _.-' (
        )  _.-'.|\\--//|.'-._  (
         )'   .'\\/o\\/o\\/'.   `(
          ) .' . \\====/ . '. (
           )  / <<    >> \\  (
            '-._/``  ``\\_.-'
      jgs     __\\'--'//__
             (((""`  `"")))
    EOC
    """))

    weapons = {'sword': 10, 'spear': 15, 'axe': 20}

    def __init__(self):
        super().__init__()

        self.x = dict()
        self.y = dict()

        self.field = [[0 for j in range(10)] for i in range(10)]

        self.invalid_mon = ('', '', 0, -1, -1)

        self.allowed_list = cowsay.list_cows()
        self.user_list = {'jgsbat': self.jgsbat}

    def add_client(self, client):
        self.x[client] = 0
        self.y[client] = 0

    def get_mon_args(self, args):
        args = shlex.split(args)

        name, hello, hp, m_x, m_y  = self.invalid_mon
        if len(args) == 0:
            args += ['default']

        if len(args) != 8:
            if "coords" not in args:
                args += ['coords', 0, 0]
            if "hp" not in args:
                args += ["hp", 100]
            if "hello" not in args:
                args += ["hello", "Hello"]

        name = args[0]

        if name not in self.allowed_list and name not in self.user_list:
            return self.invalid_mon

        i = 1
        while i < 8:
            if args[i] == 'hello':
                hello = args[i+1]
            elif args[i] == 'hp':
                try:
                    hp = int(args[i+1])
                except Exception:
                    return self.invalid_mon

                if hp <= 0:
                    return self.invalid_mon
            elif args[i] == 'coords':
                try:
                    m_x = int(args[i+1])
                    m_y = int(args[i+2])
                except Exception:
                    return self.invalid_mon

                if m_x < 0 or m_x > 9 or m_y < 0 or m_y > 9:
                    return self.invalid_mon

                i += 1
            else:
                return self.invalid_mon
            i += 2

        if i < 8:
            return self.invalid_mon

        return (name, hello, hp, m_x, m_y)

    def move(self, client, args):
        args = args.split()
        dx, dy = int(args[0]), int(args[1])

        self.x[client] = (self.x[client] + dx) % 10
        self.y[client] = (self.y[client] + dy) % 10
        x, y = self.x[client], self.y[client]

        ans = f"Moved to ({x}, {y})\n"

        if self.field[y][x] == 0:
            return ans

        hello = self.field[y][x]['hello']
        hp = self.field[y][x]['hp']
        name = self.field[y][x]['name']

        if name in self.allowed_list:
            ans += cowsay.cowsay(hello, cow=name)
        else:
            ans += cowsay.cowsay(hello, cowfile=self.user_list[name])

        return ans

    def addmon(self, client, args):
        (name, hello, hp, m_x, m_y) = self.get_mon_args(args)

        if (name, hello, hp, m_x, m_y) == self.invalid_mon:
            return "Invalid arguments\n"

        if self.field[m_y][m_x] == 0:
            self.field[m_y][m_x] = {'hello':hello, 'hp': hp, 'name': name}
            return client + f' added {name} to ({m_x}, {m_y}) saying {hello} with hp = {hp}'
        else:
            self.field[m_y][m_x] = {'hello':hello, 'hp': hp, 'name': name}
            return client + f' replaced the old monster in ({m_x}, {m_y}) with a {name} saying {hello} with hp = {hp}'


    def attack(self, client, args):
        args = shlex.split(args)

        if len(args) < 1:
            return "Type args"

        x, y = self.x[client], self.y[client]

        if self.field[y][x] == 0:
            return "No monster here"

        if args[0] != self.field[y][x]['name']:
            return f"No {args[0]} here"

        weapon = 'sword'

        if len(args) >= 2 and args[1] != 'with':
            return "Invalid arguments"

        if len(args) >= 3:
            weapon = args[2]

        if weapon != 'sword' and weapon != 'spear' and weapon != 'axe':
            return "Unknown weapon"

        hp = int(self.field[y][x]['hp'])
        name = self.field[y][x]['name']

        if weapon == 'sword':
            damage = 10
        elif weapon == 'spear':
            damage = 15
        else:
            damage = 20

        if hp < damage:
            damage = hp
        hp -= damage

        ans = client + f" attacked {name},  damage {damage} hp\n"

        if hp <= 0:
            ans += f"{name} died"
            self.field[y][x] = 0
        else:
            ans += f"{name} now has {hp}"
            self.field[y][x]['hp'] = hp

        return ans

mud = Mud()

clients = dict()
clients_names = set()

clients_conns = dict()

async def chat(reader, writer):
    global clients, clients_names, clients_conns

    me = "{}:{}".format(*writer.get_extra_info('peername'))

    name = await reader.readline()
    name = name.decode()[:-1]

    if name in clients_names:
        writer.write("off\n".encode())
        return
    else:
        mud.add_client(name)
        clients_names.add(name)
        clients[me] = name

        writer.write("in\n".encode())

    for i in clients_names:
        if i != name:
            await clients_conns[i].put(f"{name} joined the game")

    clients_conns[name] = asyncio.Queue()

    send = asyncio.create_task(reader.readline())
    receive = asyncio.create_task(clients_conns[name].get())

    while not reader.at_eof():
        done, pending = await asyncio.wait([send, receive], return_when=asyncio.FIRST_COMPLETED)

        for q in done:
            if q is send:
                query = q.result().decode().strip().split()

                if len(query) == 0:
                    writer.write("Command is incorrect.\n".encode())
                    continue
                if query[0] == 'move':
                    writer.write(mud.move(clients[me], " ".join(query[1:])).encode())
                elif query[0] == 'addmon':
                    ans = mud.addmon(clients[me], " ".join(query[1:]))

                    if ans == "Invalid arguments":
                        writer.write(ans.encode())
                    else:
                        for i in clients_names:
                            await clients_conns[i].put(ans)
                elif query[0] == 'attack':
                    ans = mud.attack(clients[me], " ".join(query[1:]))

                    if ans.startswith(clients[me]):
                        for i in clients_names:
                            await clients_conns[i].put(ans)
                    else:
                        writer.write(ans.encode())
                elif query[0] == 'quit':
                    send.cancel()
                    receive.cancel()
                    del clients[me]
                    writer.close()
                    return

                send = asyncio.create_task(reader.readline())
            elif q is receive:
                receive = asyncio.create_task(clients_conns[name].get())
                print(q)
                writer.write(f"{q.result()}\n".encode())
                await writer.drain()

    print(f'{me} Done')
    for i in clients_names:
        await clients_conns[i].put(f"{name} left the game")

    send.cancel()
    receive.cancel()
    clients_names.remove(clients[me])
    del clients[me]
    writer.close()

async def main():
    server = await asyncio.start_server(chat, '0.0.0.0', 1337)
    async with server:
        await server.serve_forever()

asyncio.run(main())