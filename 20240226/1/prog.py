import cowsay
import sys

class Monster():
    def __init__(self, x, y, hi, kind='default'):
        self.x = x
        self.y = y
        self.text = hi
        self.kind = kind

    def __str__(self):
        return cowsay.cowsay(self.text, cow=self.kind)

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
        self.monster = [[None for i in range(10)] for j in range(10)]


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

    def addmon(self, x, y, hi):
        vr_monster = self.monster[x][y]
        self.monster[x][y] = Monster(x, y, hi)
        print(f"Added monster to ({x}, {y}) saying {hi}")
        if vr_monster is not None:
            print("Replaced the old monster")
    def encounter(self, x, y):
        if self.monster[x][y] is not None:
            print(self.monster[x][y])

ar = Area()

for s in sys.stdin:
    match s.replace('\n', '').split():
        case [direction] if direction in {'up', 'down', 'left', 'right'}:
            ar.moved_to(direction)
        case ['addmon', x, y, hello]:
            try:
                x = int(x)
                y = int(y)

                if not (0 <= x <= 9):
                    raise TypeError
                if not (0 <= y <= 9):
                    raise TypeError

                ar.addmon(x, y, hello)
            except:
                print("Invalid arguments")
        case _:
            print("Invalid command")