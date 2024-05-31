from cowsay import cowsay, list_cows
import sys

class Monster():
    def __init__(self, x, y, hi, name='default'):
        self.x = x
        self.y = y
        self.text = hi
        self.name = name


    def __str__(self):
        return cowsay(self.text)


class Pers():
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


    def move_x(self, step):
        self.x += step

        if self.x == -1:
            self.x = 9
        elif self.x == 10:
            self.x = 0


    def move_y(self, step):
        self.y -= step

        if self.y == -1:
            self.y = 9
        elif self.y == 10:
            self.y = 0


class Area():
    def __init__(self):
        self.pers = Pers()
        self.monster = [[None for j in range(10)] for i in range(10)]


    def moved_to(self, direction):
        match direction:
            case 'up':
                self.pers.move_y(1)
            case 'down':
                self.pers.move_y(-1)
            case 'left':
                self.pers.move_x(-1)
            case 'right':
                self.pers.move_x(1)

        print(f"Moved to ({self.pers.x}, {self.pers.y})")

        self.encounter(self.pers.x, self.pers.y)


    def addmon(self, x, y, hi, name):
        if name not in list_cows():
            print("Cannot add unknown monster")
            return

        vr_monster = self.monster[x][y]

        self.monster[x][y] = Monster(x, y, hi, name)

        print(f"Added monster {name} to ({x}, {y}) saying {hi}")

        if vr_monster is not None:
            print("Replaced the old monster")


    def encounter(self, x, y):
        if self.monster[x][y] is not None:
            print(self.monster[x][y])


area = Area()

for s in sys.stdin:
    match s.replace('\n', '').split():
        case [direction] if direction in {'up', 'down', 'left', 'right'}:
            area.moved_to(direction)
        case ['addmon', name, x, y, hello]:
            try:
                x = int(x)
                y = int(y)

                if not (0 <= x <= 9):
                    raise TypeError
                if not (0 <= y <= 9):
                    raise TypeError

                area.addmon(x, y, hello, name)
            except:
                print("Invalid arguments")
        case _:
            print("Invalid command")