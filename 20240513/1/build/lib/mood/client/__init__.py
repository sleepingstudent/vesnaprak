"""Init file for client."""

import cowsay
import cmd
import readline
import shlex
import time
import sys
import socket
import threading
import webbrowser

from ..common import jgsbat, prompt, weapons, path_doc


class Mood(cmd.Cmd):
    """Class Mood shows the command line, autocomplete attack command and send commands to server."""

    prompt = prompt

    def __init__(self, conn, stdin=sys.stdin):
        """Initialize variables."""
        super().__init__(stdin=stdin)

        self.conn = conn

        self.allowed_list = cowsay.list_cows()
        self.user_list = {'jgsbat': jgsbat}

    def precmd(self, line):
        """Freeze console enter."""
        time.sleep(1)
        return super().precmd(line)

    def do_documentation(self, arg):
        """Open documentation."""
        webbrowser.open(path_doc)

    def do_locale(self, args):
        """Send to server message with localization info."""
        self.conn.sendall(("locale " + args + "\n").encode())

    def do_up(self, args):
        """Send to server message about moving up."""
        self.conn.sendall("move 0 -1\n".encode())

    def do_down(self, args):
        """Send to server message about moving down."""
        self.conn.sendall("move 0 1\n".encode())

    def do_right(self, args):
        """Send to server message about moving to the right."""
        self.conn.sendall("move 1 0\n".encode())

    def do_left(self, args):
        """Send to server message about moving to the left."""
        self.conn.sendall("move -1 0\n".encode())

    def do_addmon(self, args):
        """Send message about adding the monster."""
        self.conn.sendall(("addmon " + args + "\n").encode())

    def do_attack(self, args):
        """Send message about attackin the monster."""
        self.conn.sendall(("attack " + args + "\n").encode())

    def do_sayall(self, args):
        """Send message to all players."""
        self.conn.sendall(("sayall " + args + "\n").encode())

    def complete_attack(self, text, line, begidx, endidx):
        """Complete attack line."""
        res = shlex.split(line[:begidx], 0, 0)

        if len(res) <= 1:
            mon_list = list(self.user_list.keys()) + self.allowed_list
            return [c for c in mon_list if c.startswith(text)]
        elif res[-1] == 'with':
            return [c for c in weapons if c.startswith(text)]

    def do_movemonsters(self, args):
        """End cmd activity."""
        if args != "off" and args != "on":
            print("Invalid command.")

        self.conn.sendall(("movemonsters " + args + "\n").encode())

    def do_q(self, args):
        """End cmd activity."""
        return True

    def do_quit(self, args):
        """End cmd activity."""
        return True

    def do_EOF(self, args):
        """End cmd activity."""
        return True


def recieve(cmd):
    """Recieve the messages from server in another thread."""
    while cmd.conn is not None:
        data = ""

        while len(new := cmd.conn.recv(1024)) == 1024:
            data += new.decode()

        data += new.decode()

        print(f"\n{data.strip()}\n{cmd.prompt}{readline.get_line_buffer()}", end='', flush=True)


def main():
    """Start client."""
    host = "localhost"
    port = 1337
    name = "My name\n"
    file = ""

    for i in range(len(sys.argv)):
        if sys.argv[i] == '--file':
            file = "" if len(sys.argv) < i + 2 else sys.argv[i + 1]
        elif sys.argv[i] == '--name':
            name = "my name\n" if len(sys.argv) < i + 2 else sys.argv[i + 1] + "\n"
        elif sys.argv[i] == '--host':
            host = 'localhost' if len(sys.argv) < i + 2 else sys.argv[i + 1]
        elif sys.argv[i] == '--port':
            port = 1337 if len(sys.argv) < i + 2 else int(sys.argv[i + 1])

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(name.encode())
        is_name = s.recv(1024).decode()
        if (is_name[:-1] == "off"):
            print("The name is busy")
            sys.exit(0)

        print(f"{name[:-1]}, Welcome to Python-mood 0.1 !!!")
        if file != "":
            fd = open(file, 'r')
            mood = Mood(s, fd)
            mood.prompt = ""
            mood.use_rawinput = False
        else:
            mood = Mood(s)

        rec = threading.Thread(target=recieve, args=(mood,))
        rec.daemon = True
        rec.start()

        mood.cmdloop()
