"""Initial file for server."""
import cowsay
import asyncio
import shlex
import random

import gettext
import locale

from ..common import jgsbat, weapons


LOCALES = {
    ("ru_RU", "UTF-8"): gettext.translation("mood", "po1", ["ru_RU.UTF-8"], fallback=True),
    ("en_US", "UTF-8"): gettext.NullTranslations(),
    ("en_GB", "UTF-8"): gettext.NullTranslations(),
}

SIZE = 10

clients_loc = dict()


def ngettext(client, *text):
    """Get translation function by chosen locale."""
    return LOCALES[clients_loc[client]].ngettext(*text)


def _(client, text):
    """Get translation function by chosen locale."""
    return LOCALES[clients_loc[client]].gettext(text)


class Mood():
    """Check correctness of clients commands and execute them."""

    jgsbat = jgsbat

    weapons = weapons

    not_move_rand_mon = False

    def __init__(self):
        """Set initial values and allowed cows."""
        super().__init__()

        self.clients = set()
        self.x = dict()
        self.y = dict()

        self.field = [[0 for j in range(SIZE)] for i in range(SIZE)]

        self.invalid_mon = ('', '', 0, -1, -1)

        self.allowed_list = cowsay.list_cows()
        self.user_list = {'jgsbat': self.jgsbat}
        self.taken_cows = set()

    def add_client(self, client):
        """
        Add client to the field.

        :param client: nickname of client
        """
        self.clients.add(client)

        self.x[client] = 0
        self.y[client] = 0

    def get_mon_args(self, args):
        """
        Check the correctness of arguments from the "addmon" command.

        :param args: string with args
        """
        # print(args)
        args = shlex.split(args)

        name, hello, hp, m_x, m_y = self.invalid_mon
        if len(args) == 0:
            args += ['default']

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
        # print(args)
        while i < len(args):
            # print(args[i])
            if args[i] == 'hello':
                hello = args[i + 1] if i + 1 < len(args) and args[i + 1] not in ['hp', 'coords'] else ""
                i += 1

                while i + 1 < len(args) and args[i + 1] not in ['hp', 'coords']:
                    hello += " " + args[i+1]
                    i += 1

                i -= 1
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
        # print(m_x, m_y)
        return (name, hello, hp, m_x, m_y)

    def move(self, client, args):
        """
        Move user to the next cell.

        :param client: nickname of client who will recieve msg
        :param args: string with args
        """
        args = args.split()
        dx, dy = int(args[0]), int(args[1])

        self.x[client] = (self.x[client] + dx) % SIZE
        self.y[client] = (self.y[client] + dy) % SIZE
        x, y = self.x[client], self.y[client]

        ans = _(client, "Moved to ({}, {})\n").format(x, y)

        if self.field[y][x] == 0:
            return ans

        hello = self.field[y][x]['hello']
        # hp = self.field[y][x]['hp']
        name = self.field[y][x]['name']

        if name in self.allowed_list:
            ans += cowsay.cowsay(hello, cow=name)
        else:
            ans += cowsay.cowsay(hello, cowfile=self.user_list[name])

        return ans

    def addmon(self, client, args):
        """
        Add monster to the cell.

        :param client: nickname of client who will recieve msg
        :param args: string with args
        """
        (name, hello, hp, m_x, m_y) = self.get_mon_args(args)

        if (name, hello, hp, m_x, m_y) == self.invalid_mon:
            return (len(self.taken_cows), _(client, "Invalid arguments\n"))

        msg_all = dict()
        for i in self.clients:
            if self.field[m_y][m_x] == 0:
                ans = '"' + client + '"' + _(i, " added {} to ({}, {}) saying {} ").format(name, \
                                                                                           m_x, m_y, \
                                                                                           hello)
                ans += ngettext(i, "with hp = {}", "with hp = {}", hp).format(hp)
            else:
                ans = '"' + client + '"' + _(i, ' replaced the old monster in ')
                ans += ngettext(i, "({}, {}) with a {} saying {} with hp = {}", \
                                "({}, {}) with a {} saying {} with hp = {}", \
                                hp).format(m_x, m_y, name, hello, hp)

            msg_all[i] = ans

        self.field[m_y][m_x] = {'hello': hello, 'hp': hp, 'name': name}
        self.taken_cows.add((m_y, m_x))

        return (len(self.taken_cows), msg_all)

    def attack(self, client, args):
        """
        Attack monster in the current cell.

        :param client: nickname of client who will recieve msg
        :param args: string with args
        """
        args = shlex.split(args)

        if len(args) < 1:
            return _(client, "Type args")

        x, y = self.x[client], self.y[client]

        if self.field[y][x] == 0:
            return _(client, "No monster here")

        if args[0] != self.field[y][x]['name']:
            return _(client, "No {} here").format(args[0])

        weapon = 'sword'

        if len(args) >= 2 and args[1] != 'with':
            return _(client, "Invalid arguments")

        if len(args) >= 3:
            weapon = args[2]

        if weapon != 'sword' and weapon != 'spear' and weapon != 'axe':
            return _(client, "Unknown weapon")

        hp = int(self.field[y][x]['hp'])
        name = self.field[y][x]['name']

        damage = weapons[weapon]

        if hp < damage:
            damage = hp
        hp -= damage

        msg_all = dict()
        fl = True
        for i in self.clients:
            ans = '"' + client + '"' + ngettext(i, " attacked {},  damage {} hp\n", \
                                                " attacked {},  damage {} hp\n", hp).format(name, \
                                                                                            damage)

            if hp <= 0:
                ans += _(i, "{} died").format(name)
                if fl:
                    self.field[y][x] = 0
                    self.taken_cows.remove((y, x))
            else:
                ans += ngettext(i, "{} now has {} hp.", "{} now has {} hp.", hp).format(name, hp)
                if fl:
                    self.field[y][x]['hp'] = hp

            fl = False
            msg_all[i] = ans

        return (len(self.taken_cows), msg_all)

    async def move_random_mon(self):
        """Move random monster to the next cell by timer."""
        await asyncio.sleep(30)

        while True:
            if len(self.taken_cows) == 0 or len(self.taken_cows) == SIZE ** 2:
                return ([], "", [])

            cell = random.choice(list(self.taken_cows))
            move = random.choice(['up', 'down', 'right', 'left'])

            if move == 'up':
                new_cell = ((cell[0] - 1) % SIZE, cell[1])
            elif move == 'down':
                new_cell = ((cell[0] + 1) % SIZE, cell[1])
            elif move == 'right':
                new_cell = (cell[0], (cell[1] + 1) % SIZE)
            else:
                new_cell = (cell[0], (cell[1] - 1) % SIZE)

            if self.field[new_cell[0]][new_cell[1]] != 0:
                continue

            if self.not_move_rand_mon:
                return ([], "", [])

            mon_name = self.field[cell[0]][cell[1]]['name']
            hello = self.field[cell[0]][cell[1]]['hello']

            if mon_name in self.allowed_list:
                msg = cowsay.cowsay(hello, cow=mon_name)
            else:
                msg = cowsay.cowsay(hello, cowfile=self.user_list[mon_name])

            self.field[new_cell[0]][new_cell[1]] = self.field[cell[0]][cell[1]]
            self.field[cell[0]][cell[1]] = 0

            self.taken_cows.remove(cell)
            self.taken_cows.add(new_cell)

            names_list = []
            msg_all = []
            for name in self.clients:
                if self.x[name] == new_cell[1] and self.y[name] == new_cell[0]:
                    names_list.append(name)

                if move == 'up':
                    msg_all.append(_(name, "{} moved one cell up").format(mon_name, move))
                elif move == 'down':
                    msg_all.append(_(name, "{} moved one cell down").format(mon_name, move))
                elif move == 'right':
                    msg_all.append(_(name, "{} moved one cell right").format(mon_name, move))
                else:
                    msg_all.append(_(name, "{} moved one cell left").format(mon_name, move))

            return (msg_all, msg, names_list)


mood = Mood()

cow_num = 0

clients = dict()
clients_names = set()
clients_conns = dict()

mon_task = 1
fl = False
moving = True


async def chat(reader, writer):
    """
    Check correctness of clients commands and executes them.

    :param reader: read data from IO stream
    :param writer: write data to IO stream
    """
    global mood, cow_num, clients, clients_names, clients_conns, clients_loc, mon_task, fl, moving

    me = "{}:{}".format(*writer.get_extra_info('peername'))
    name = await reader.readline()
    name = name.decode()[:-1]

    if name in clients_names:
        writer.write("off\n".encode())
        return
    else:
        mood.add_client(name)
        clients_names.add(name)
        clients[me] = name

        writer.write("in\n".encode())

    clients_loc[name] = ("en_US", "UTF-8")

    for i in clients_names:
        if i != name:
            await clients_conns[i].put(_(name, "{} joined the game.").format(name))

    clients_conns[name] = asyncio.Queue()

    send = asyncio.create_task(reader.readline())
    receive = asyncio.create_task(clients_conns[name].get())

    while not reader.at_eof():
        if fl is True and moving is True:
            done, pending = await asyncio.wait([send, receive, mon_task], return_when=asyncio.FIRST_COMPLETED)
        else:
            done, pending = await asyncio.wait([send, receive], return_when=asyncio.FIRST_COMPLETED)

        for q in done:
            if q is mon_task:
                msg_all, msg, cl = q.result()

                if len(msg_all) != 0:
                    for i, ms in zip(clients_names, msg_all):
                        if i in cl:
                            await clients_conns[i].put(ms + "\n" + msg)
                        else:
                            await clients_conns[i].put(ms)
                mon_task = asyncio.create_task(mood.move_random_mon())
            elif q is send:
                query = q.result().decode().strip().split()
                # print(query)

                if len(query) == 0:
                    writer.write(_(name, "Command is incorrect.\n").encode())
                    continue
                if query[0] == 'locale':
                    try:
                        cur = locale.getlocale()
                        locale.setlocale(locale.LC_ALL, (query[1], query[2]))
                        clients_loc[name] = (query[1], query[2])
                        writer.write(_(name, "Set up locale: {} {}\n").format(query[1], query[2]).encode())
                    except Exception:
                        locale.setlocale(locale.LC_ALL, cur)
                        writer.write(_(name, "Invalid locale: {} {}\n").format(query[1], query[2]).encode())
                elif query[0] == 'move':
                    writer.write(mood.move(clients[me], " ".join(query[1:])).encode())
                elif query[0] == 'addmon':
                    cur_cow_num, ans = mood.addmon(clients[me], " ".join(query[1:]))

                    if type(ans) is str:
                        writer.write(ans.encode())
                    else:
                        if cur_cow_num > 0 and moving is True:
                            mon_task = asyncio.create_task(mood.move_random_mon())
                            fl = True

                        cow_num = cur_cow_num

                        for i in clients_names:
                            await clients_conns[i].put(ans[i])
                elif query[0] == 'attack':
                    ans = mood.attack(clients[me], " ".join(query[1:]))

                    if type(ans) is str:
                        writer.write(ans.encode())
                    else:
                        cow_num, ans = ans

                        if cow_num == 0:
                            fl = False
                            mood.not_move_rand_mon = True

                        for i in clients_names:
                            await clients_conns[i].put(ans[i])
                elif query[0] == 'sayall':
                    for i in clients_names:
                        await clients_conns[i].put(name + ": " + " ".join(query[1:]))
                elif query[0] == 'movemonsters':
                    if query[1] == "on" and moving is False:
                        moving = True
                        mood.not_move_rand_mon = False

                        if len(asyncio.all_tasks()) == 2:
                            mon_task = asyncio.create_task(mood.move_random_mon())

                        for i in clients_names:
                            await clients_conns[i].put(_(i, "Moving monsters: on"))
                    elif query[1] == "off" and moving is True:
                        moving = False
                        mood.not_move_rand_mon = True

                        for i in clients_names:
                            await clients_conns[i].put(_(i, "Moving monsters: off"))
                elif query[0] == 'quit':
                    send.cancel()
                    receive.cancel()
                    del clients[me]
                    writer.close()
                    return
                send = asyncio.create_task(reader.readline())
            elif q is receive:
                receive = asyncio.create_task(clients_conns[name].get())
                writer.write("{}\n".format(q.result()).encode())
                await writer.drain()

    # print(f'{me} Done')
    for i in clients_names:
        await clients_conns[i].put(_(i, "{} left the game.").format(name))

    send.cancel()
    receive.cancel()
    clients_names.remove(clients[me])
    del clients[me]
    writer.close()


async def run_server():
    """Run async server."""
    server = await asyncio.start_server(chat, '0.0.0.0', 1337)
    async with server:
        await server.serve_forever()


def main():
    """Start server."""
    asyncio.run(run_server())
