import socket
import sys
import cowsay


x = 0
y = 0

field = [[0 for j in range(10)] for i in range(10)]

default = ('', '', 0, -1, -1)

host = "localhost" if len(sys.argv) < 2 else sys.argv[1]
port = 1337 if len(sys.argv) < 3 else int(sys.argv[2])

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((host, port))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)

        while data := conn.recv(1024):
            data = data.decode().split()

            if data[0] == 'move':
                '''move m_x m_y'''
                x = (x + int(data[1])) % 10
                y = (y + int(data[2])) % 10

                if field[y][x] == 0:
                    conn.sendall(f"empty {x} {y}\n".encode())
                else:
                    conn.sendall(f"monster {x} {y} {field[y][x]['name']} {field[y][x]['hello']}\n".encode())
            elif data[0] == 'addmon':
                '''addmon <monster_name> <m_x> <m_y> <hp> <hello>'''
                name, m_x, m_y, hp, hello = data[1], int(data[2]), int(data[3]), int(data[4]), data[5]

                if field[m_y][m_x] == 0:
                    conn.sendall("add\n".encode())
                else:
                    conn.sendall("replace\n".encode())

                field[m_y][m_x] = {'name': name, 'hp': hp, 'hello': hello}
            elif data[0] == 'attack':
                '''attack <name> <damage>'''

                name = data[1]
                damage = int(data[2])

                if field[y][x] == 0:
                    conn.sendall("empty 0 0\n".encode())
                elif field[y][x]['name'] != name:
                    conn.sendall("wrong_name 0 0\n".encode())
                else:
                    if field[y][x]['hp'] <= damage:
                        damage = field[y][x]['hp']
                        hp = 0
                        field[y][x] = 0
                    else:
                        hp = field[y][x]['hp'] - damage
                        field[y][x]['hp'] -= damage

                    conn.sendall(f"attack {damage} {hp}\n".encode())
            else:
                print("Invalid command")