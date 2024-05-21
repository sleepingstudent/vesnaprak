import cowsay
from io import StringIO
import shlex


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

field = [[0 for j in range(10)] for i in range(10)]
allowed_list = cowsay.list_cows()
user_list = {'jgsbat': jgsbat}


def encounter(x, y):
    hello = field[y][x]['hello']
    hp = field[y][x]['hp']
    name = field[y][x]['name']

    if name in allowed_list:
        print(cowsay.cowsay(hello, cow=name))
    else:
        print(cowsay.cowthink(hello, cowfile=user_list[name]))

print("<<< Welcome to Python-MUD 0.1 >>>")

x, y = 0, 0

while inp := input():
    inp = shlex.split(inp)

    moved = 0
    if inp[0] == 'up':
        y = (y - 1) % 10
        moved = 1
    elif inp[0] == 'down':
        y = (y + 1) % 10
        moved = 1
    elif inp[0] == 'right':
        x = (x + 1) % 10
        moved = 1
    elif inp[0] == 'left':
        x = (x - 1) % 10
        moved = 1

    if moved == 1:
        print(f'Moved to ({x}, {y})')

        if field[y][x] != 0:
            encounter(x, y)
    else:
        if inp[0] == 'addmon':
            if len(inp) != 9:
                print("Invalid arguments")
                continue

            name = inp[1]

            if name not in allowed_list and inp[1] not in user_list:
                print("Invalid arguments")
                continue

            hello = ''
            hp = 0
            m_x, m_y = 0, 0

            i = 2
            while i < 9:
                if inp[i] == 'hello':
                    hello = inp[i+1]

                    i += 2
                elif inp[i] == 'hp':
                    try:
                        hp = int(inp[i+1])
                    except Exception:
                        break

                    if hp <= 0:
                        break

                    i += 2
                elif inp[i] == 'coords':
                    try:
                        m_x = int(inp[i+1])
                        m_y = int(inp[i+2])
                    except Exception:
                        break

                    if m_x < 0 or m_x > 9 or m_y < 0 or m_y > 9:
                        break

                    i += 3
                else:
                    print("Invalid arguments")
                    break

            if i < 9:
                continue

            if field[m_y][m_x] == 0:
                print(f'Added monster to ({m_x}, {m_y}) saying {hello}')
            else:
                print(f'Replaced the old monster')

            field[m_y][m_x] = {'hello':hello, 'hp': hp, 'name': name}
        else:
            print('Invalid command')
