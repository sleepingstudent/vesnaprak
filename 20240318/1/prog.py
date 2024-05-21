import cowsay
import cmd
from io import StringIO
import shlex


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

    weapons = ['sword', 'spear', 'axe']

    prompt = ':->'

    def __init__(self):
        super().__init__()

        self.x = 0
        self.y = 0

        self.field = [[0 for j in range(10)] for i in range(10)]

        self.default = ('', '', 0, -1, -1)

        self.allowed_list = cowsay.list_cows()
        self.user_list = {'jgsbat': self.jgsbat}


    def get_mon_args(self, args):
        args = shlex.split(args)

        name, hello, hp, m_x, m_y  = self.default

        if len(args) != 8:
            print("Invalid arguments")
            return self.default

        name = args[0]

        if name not in self.allowed_list and name not in self.user_list:
            print("Invalid arguments")
            return self.default

        i = 1
        while i < 8:
            if args[i] == 'hello':
                hello = args[i+1]
            elif args[i] == 'hp':
                try:
                    hp = int(args[i+1])
                except Exception:
                    return self.default

                if hp <= 0:
                    return self.default
            elif args[i] == 'coords':
                try:
                    m_x = int(args[i+1])
                    m_y = int(args[i+2])
                except Exception:
                    return self.default

                if m_x < 0 or m_x > 9 or m_y < 0 or m_y > 9:
                    print("Invalid arguments")
                    return self.default

                i += 1
            else:
                print("Invalid arguments")
                return self.default
            i += 2

        if i < 8:
            return self.default

        return (name, hello, hp, m_x, m_y)


    def move_mon(self, name, hello, hp, m_x, m_y):
        if (name, hello, hp, m_x, m_y) == self.default:
            return

        if self.field[m_y][m_x] == 0:
            print(f'Added monster to ({m_x}, {m_y}) saying {hello}')
        else:
            print(f'Replaced the old monster')

        self.field[m_y][m_x] = {'hello':hello, 'hp': hp, 'name': name}


    def encounter(self, x, y):
        print(f'Moved to ({x}, {y})')

        if self.field[y][x] == 0:
            return

        hello = self.field[y][x]['hello']
        hp = self.field[y][x]['hp']
        name = self.field[y][x]['name']

        if name in self.allowed_list:
            print(cowsay.cowsay(hello, cow=name))
        else:
            print(cowsay.cowsay(hello, cowfile=self.user_list[name]))


    def move_up(self):
        self.y = (self.y - 1) % 10
        self.encounter(self.x, self.y)


    def move_down(self):
        self.y = (self.y + 1) % 10
        self.encounter(self.x, self.y)


    def move_right(self):
        self.x = (self.x + 1) % 10
        self.encounter(self.x, self.y)


    def move_left(self):
        self.x = (self.x - 1) % 10
        self.encounter(self.x, self.y)


    def do_up(self, args):
        self.move_up()


    def do_down(self, args):
        self.move_down()


    def do_right(self, args):
        self.move_right()


    def do_left(self, args):
        self.move_left()


    def do_addmon(self, args):
        self.move_mon(*self.get_mon_args(args))


    def do_attack(self, args):
        args = shlex.split(args)

        if len(args) < 1:
            print("Type args")
            return

        if self.field[self.y][self.x] == 0:
            print("No monster here")
            return

        if args[0] != self.field[self.y][self.x]['name']:
            print(f"No {args[0]} here")

        weapon = 'sword'

        if len(args) >= 2 and args[1] != 'with':
            print("Invalid arguments")
            return

        if len(args) >= 3:
            weapon = args[2]

        if weapon != 'sword' and weapon != 'spear' and weapon != 'axe':
            print("Unknown weapon")
            return

        hp = int(self.field[self.y][self.x]['hp'])
        name = self.field[self.y][self.x]['name']

        if weapon == 'sword':
            damage = 10
        elif weapon == 'spear':
            damage = 15
        else:
            damage = 20


        if hp < damage:
            damage = hp
        hp -= damage

        print(f"Attacked {name},  damage {damage} hp")

        if hp <= 0:
            print(f"{name} died")
            self.field[self.y][self.x] = 0
        else:
            print(f"{name} now has {hp}")
            self.field[self.y][self.x]['hp'] = hp


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
    Mud().cmdloop()    
