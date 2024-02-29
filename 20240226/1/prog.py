import cowsay

class Monster():
    def __init__(self, x, y, hi, kind='default'):
        pass

class Pers():
    def __init__(self):
        self.x = 0
        self.y = 0

    def moved_to(self, ):
        pass

    def move_x(self, direction):
        self.x += direction

        if self.x == -1:
            self.x = 9
        elif self.x == 10:
            self.x = 0

    def move_y(self, direction):
        self.y += direction
        if self.y == -1:
            self.y = 9
        elif self.y == 10:
            self.y = 0