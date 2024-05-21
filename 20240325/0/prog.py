from http.server import test, SimpleHTTPRequestHandler
import socket


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
test(SimpleHTTPRequestHandler, bind=s.getsockname()[0], port=8001)
print(s.getsockname()[0])
s.close()
