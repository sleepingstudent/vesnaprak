import cowsay
import cmd
from io import StringIO
import sys
import socket
import shlex
import threading
import readline

class Mud(cmd.Cmd):
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

    prompt = ':->'

    def __init__(self, conn):
        super().__init__()

        self.conn = conn

        self.allowed_list = cowsay.list_cows()
        self.user_list = {'jgsbat': self.jgsbat}

    def do_up(self, args):
        self.conn.sendall("move 0 -1\n".encode())

    def do_down(self, args):
        self.conn.sendall("move 0 1\n".encode())

    def do_right(self, args):
        self.conn.sendall("move 1 0\n".encode())

    def do_left(self, args):
        self.conn.sendall("move -1 0\n".encode())

    def do_addmon(self, args):
        self.conn.sendall(("addmon " + args + "\n").encode())

    def do_attack(self, args):
        self.conn.sendall(("attack " + args + "\n").encode())

    def complete_attack(self, text, line, begidx, endidx):
        res = shlex.split(line[:begidx], 0, 0)
        if len(res) <= 1:
            mon_list = list(self.user_list.keys()) + self.allowed_list
            return [c for c in mon_list if c.startswith(text)]
        elif res[-1] == 'with':
            return [c for c in self.weapons if c.startswith(text)]

    def do_EOF(self, args):
        return True


def recieve(cmd):
    while cmd.conn is not None:
        data = ""

        while len(new := cmd.conn.recv(1024)) == 1024:
            data += new.decode()

        data += new.decode()

        print(f"\n{data.strip()}\n{cmd.prompt}{readline.get_line_buffer()}", end='', flush=True)

if __name__ == "__main__":
    print("<<< Welcome to Python-MUD 0.1 >>>")

    name = "my name\n" if len(sys.argv) < 2 else sys.argv[1] + "\n"
    host = "localhost" if len(sys.argv) < 3 else sys.argv[2]
    port = 1337 if len(sys.argv) < 4 else int(sys.argv[3])

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        print(name)
        s.sendall(name.encode())
        is_name = s.recv(1024).decode()
        if (is_name == "off"):
            print("The name is busy")
            sys.exit(0)

        print(f"{name[:-1]}, Welcome to Python-MUD 0.1 !!!")
        mud = Mud(s)

        recieve = threading.Thread(target=recieve, args=(mud,))
        recieve.daemon = True
        recieve.start()

        mud.cmdloop()   
