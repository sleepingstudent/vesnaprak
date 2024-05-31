"""Client runner."""

from .client import InterGame, serv
import sys
import socket
import threading


if len(sys.argv) != 2:
    print('wrong arguments')
    print('example: python3 -m client username')
    sys.exit()

print("<<< Welcome to Python-MUD 0.1 >>>")

host = "localhost"
port = 1337

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))

s.sendall(f'{sys.argv[1]}\n'.encode())

answer = s.recv(1024).decode().strip()

if answer == 'no':
    s.sendall(b'end\n')
    s.close()
    print(f'User named {sys.argv[1]} is already in the game')
    sys.exit()

cmdl = InterGame(s)
serv_talk = threading.Thread(target=serv, args=(cmdl, s))
serv_talk.start()

cmdl.cmdloop()

s.close()
