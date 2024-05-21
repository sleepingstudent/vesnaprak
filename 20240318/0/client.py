import sys
import socket
import cmd


host = "localhost" if len(sys.argv) < 2 else sys.argv[1]
port = 1337 if len(sys.argv) < 3 else int(sys.argv[2])


class Client(cmd.Cmd):
    def __init__(self, socket):
        super().__init__()
        self.socket = socket

    def do_print(self, args):
        self.socket.sendall(args.encode())
        print(s.recv(1024).rstrip().decode())

    def do_info(self, args):
        args = args.split()
        if len(args) == 1 and args[0] == 'host':
            self.socket.sendall(str(host).encode())
        elif len(args) == 1 and args[0] == 'port':
            self.socket.sendall(str(port).encode())
        else:
            self.socket.sendall((str(host)+':'+str(port)).encode())
        print(s.recv(1024).rstrip().decode())

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((host, port))
    
    Client(s).cmdloop()
