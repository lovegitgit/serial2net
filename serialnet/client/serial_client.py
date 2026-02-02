import socket
import threading
import sys

class SerialNetClient:
    def __init__(self, host, port):
        self.sock = socket.create_connection((host, port))

    def start(self):
        def recv_loop():
            while True:
                data = self.sock.recv(4096)
                if not data:
                    break
                sys.stdout.buffer.write(data)
                sys.stdout.flush()

        threading.Thread(target=recv_loop, daemon=True).start()

        while True:
            data = sys.stdin.buffer.read(1)
            if not data:
                break
            self.sock.sendall(data)
