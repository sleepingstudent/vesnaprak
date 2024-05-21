'''def sqroots(coeffs:str, s: socket.socket) -> str:
    s.sendall((coeffs + "\n").encode())'''
def sqroots(coeffs:str) -> str:
    a,b,c = map(float, coeffs.split())
    d = b * b - 4 * a * c
    x_1 = (-b + d ** 0.5) / 2 / a
    x_2 = (-b - d ** 0.5) / 2 / a
    return str(x_1) + " " + str(x_2)

import asyncio
import socket

async def echo(reader, writer):
    data = (await reader.readline()).decode().strip()
    try:
        res = sqroots(data)
    except Exception:
        res = ""
    writer.write(f'{res}\n'.encode())
    writer.close()
    await writer.wait_closed()

async def _serve(port):
    server = await asyncio.start_server(echo, '0.0.0.0', 1337)
    async with server:
        await server.serve_forever()

def server(port):
    asyncio.run(_serve(port))

def sqrootnet(coeffs:str, s: socket.socket) -> str:
    s.sendall((coeffs + "\n").encode())
    return s.recv(128).decode().strip()

def client(port):
    coeffs = input(">")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("localhost", port))
        res = sqrootnet(coeffs, s)
    print(res)
