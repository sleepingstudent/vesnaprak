"""Client for MUD."""

from cowsay import list_cows
import shlex
import cmd
import sys
import readline
import socket
import threading


if 'libedit' in readline.__doc__:
    readline.parse_and_bind("bind ^I rl_complete")
else:
    readline.parse_and_bind("tab: complete")


def serv(cmdl, s):
    """serv.

    :param cmdl: cmd name
    :param s: socket
    """
    try:
        while msg := s.recv(1024).rstrip().decode():
            buf = readline.get_line_buffer().split('\n')[-1]
            print(f"\n\n{msg}\n\n{cmdl.prompt}{buf}", end='', flush=True)
    except Exception:
        pass


class InterGame(cmd.Cmd):
    """InterGame."""

    prompt = '~> '

    def __init__(self, s):
        """__init__.

        :param s: socket
        """
        super().__init__()

        self.weapon = {'sword': 10, 'spear': 15, 'axe': 20}
        self.name_of_monster = list_cows() + ["jgsbat"]

        self.s = s

    def default(self, args):
        """default.

        :param args: args
        """
        print("Invalid command")

    def do_up(self, args):
        """do_up.

        :param args: args
        """
        self.s.sendall("move 0 1\n".encode())

    def do_down(self, args):
        """do_down.

        :param args: args
        """
        self.s.sendall("move 0 -1\n".encode())

    def do_left(self, args):
        """do_left.

        :param args: args
        """
        self.s.sendall("move -1 0\n".encode())

    def do_right(self, args):
        """do_right.

        :param args: args
        """
        self.s.sendall("move 1 0\n".encode())

    def do_addmon(self, args):
        """do_addmon.

        :param args: args
        """
        a = shlex.split(args)
        monster_name, hello_string, hitpoints, x, y = '', '', 0, 0, 0
        h_id, hit_id, x_id, y_id = [-1] * 4
        fl = [False] * 3
        m_id = 28
        for i in range(len(a) - 1):
            if a[i] == 'hello':
                h_id = i + 1
                m_id -= (i + i + 1)
                fl[0] = True
            elif a[i] == 'hp':
                hit_id = i + 1
                m_id -= (i + i + 1)
                fl[1] = True
            elif a[i] == 'coords' and i != len(a) - 2:
                x_id = i + 1
                y_id = i + 2
                m_id -= (i + i + 1 + i + 2)
                fl[2] = True

        if not all(fl):
            print(h_id, hit_id, x_id, y_id)
            print("Invalid command")
            return

        monster_name = a[m_id]
        hello_string = a[h_id]
        hitpoints = a[hit_id]
        x = a[x_id]
        y = a[y_id]

        try:
            x = int(a[x_id])
            y = int(a[y_id])
            hitpoints = int(a[hit_id])

            if not (0 <= x <= 9):
                raise ValueError
            if not (0 <= y <= 9):
                raise ValueError
            if hitpoints <= 0:
                raise ValueError

            self.s.sendall(f"addmon {x} {y} '{hello_string}' {monster_name} {hitpoints}\n".encode())
        except Exception:
            print("Invalid arguments")

    def do_attack(self, args):
        """do_attack.

        :param args: args
        """
        a = shlex.split(args)

        monster_name = a[0]

        weapon = 'sword'

        if len(a) > 2 and a[1] == 'with' and a[2] in {'sword', 'spear', 'axe'}:
            weapon = a[2]
        elif len(a) >= 2 and a[1] == 'with':
            print("Unknown weapon")
            return

        self.s.sendall(f"attack {monster_name} with {weapon}\n".encode())

    def do_sayall(self, args):
        """do_sayall.

        :param args: args
        """
        self.s.sendall(f'sayall {args}\n'.encode())

    def complete_attack(self, text, line, begidx, endidx):
        """complete_attack.

        :param text: text
        :param line: line
        :param begidx: begin index
        :param endidx: end index
        """
        a = shlex.split(line[:begidx])

        if a[-1] == 'with':
            return [c for c in self.weapon if c.startswith(text)]
        elif a[-1] == 'attack':
            return [c for c in self.name_of_monster if c.startswith(text)]

    def do_EOF(self, args):
        """do_EOF.

        :param args: args
        """
        self.s.sendall("\0\n".encode())
        print()
        return True
