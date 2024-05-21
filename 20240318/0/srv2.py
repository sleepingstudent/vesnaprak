import socket
import sys

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

            if data[0] == 'print':
                conn.sendall((' '.join(data[1:])+'\n').encode())
            elif data[0] == 'info':
                if len(data) > 1 and data[1] == 'host':
                    conn.sendall((str(addr[0])+'\n').encode())
                elif len(data) > 1 and data[1] == 'port':
                    conn.sendall((str(addr[1])+'\n').encode())
                else:
                    conn.sendall((str(addr)+'\n').encode())

