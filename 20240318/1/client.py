import cowsay
import cmd
from io import StringIO
import sys
import socket
import shlex


host = "localhost" if len(sys.argv) < 2 else sys.argv[1]
port = 1337 if len(sys.argv) < 3 else int(sys.argv[2])

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

        self.x = 0
        self.y = 0

        self.field = [[0 for j in range(10)] for i in range(10)]

        self.invalid_mon = ('', '', 0, -1, -1)
        # self.default_mon = ('default', 'Hello', 100, 0, 0)
        self.allowed_list = cowsay.list_cows()
        self.user_list = {'jgsbat': self.jgsbat}

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
            print("Invalid arguments")
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
                    print("Invalid arguments")
                    return self.invalid_mon

                i += 1
            else:
                print("Invalid arguments")
                return self.invalid_mon
            i += 2

        if i < 8:
            return self.invalid_mon

        return (name, hello, hp, m_x, m_y)

    '''
    def move_mon(self, name, hello, hp, m_x, m_y):
        if (name, hello, hp, m_x, m_y) == self.invalid_mon:
            return

        self.conn.sendall(f"addmon {name} {m_x} {m_y} {hp} {hello}\n".encode())
        data = self.conn.recv(1024).decode().split()

        if self.field[m_y][m_x] == 0:
            print(f'Added monster to ({m_x}, {m_y}) saying {hello}')
        else:
            print(f'Replaced the old monster')

        self.field[m_y][m_x] = {'hello':hello, 'hp': hp, 'name': name}
    '''

    def encounter(self, dx, dy):
        self.conn.sendall(f"move {dx} {dy}\n".encode())
        data = self.conn.recv(1024).decode().split()

        x, y = data[1], data[2]
        print(f'Moved to ({x}, {y})')

        if data[0] == 'monster' and data[3] in self.allowed_list:
            print(cowsay.cowsay(" ".join(data[4:]), cow=data[3]))
        elif data[0] == 'monster':
            print(cowsay.cowsay(" ".join(data[4:]), cowfile=self.user_list[data[3]]))

    def do_up(self, args):
        self.encounter(0, -1)

    def do_down(self, args):
        self.encounter(0, 1)

    def do_right(self, args):
        self.encounter(1, 0)

    def do_left(self, args):
        self.encounter(-1, 0)

    def do_addmon(self, args):
        (name, hello, hp, m_x, m_y) = self.get_mon_args(args)

        if (name, hello, hp, m_x, m_y) == self.invalid_mon:
            return

        self.conn.sendall(f"addmon {name} {m_x} {m_y} {hp} {hello}\n".encode())
        data = self.conn.recv(1024).decode().split()

        if data[0] == "add":
            print(f'Added monster to ({m_x}, {m_y}) saying {hello}')
        else:
            print("Replaced the old monster")

    def do_attack(self, args):
        args = shlex.split(args)

        if len(args) < 1:
            print("Type args")
            return

        name = args[0]
        if name not in self.allowed_list and name not in self.user_list:
            print("No such monster")
            return

        if len(args) >= 2 and args[1] != 'with':
            print("Invalid arguments")
            return

        weapon = 'sword'
        if len(args) >= 3:
            weapon = args[2]

        if weapon not in self.weapons:
            print("Unknown weapon")
            return

        damage = self.weapons[weapon]

        self.conn.sendall(f"attack {name} {damage}\n".encode())
        ans, damage, hp = tuple(self.conn.recv(1024).decode().split())

        if ans == 'empty':
            print("No monster here")
            return
        elif ans == 'wrong_name':
            print(f"No {name} here")
            return
        else:
            print(f"Attacked {name},  damage {damage} hp")
            if hp == '0':
                print(f"{name} died")
            else:
                print(f"{name} now has {hp}")

    def complete_attack(self, text, line, begidx, endidx):
        res = shlex.split(line[:begidx], 0, 0)
        if len(res) <= 1:
            mon_list = list(self.user_list.keys()) + self.allowed_list
            return [c for c in mon_list if c.startswith(text)]
        elif res[-1] == 'with':
            return [c for c in self.weapons if c.startswith(text)]

    def do_EOF(self, args):
        return True


if __name__ == "__main__":
    print("<<< Welcome to Python-MUD 0.1 >>>")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        Mud(s).cmdloop()   
