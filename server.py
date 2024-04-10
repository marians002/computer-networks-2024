import socket
import threading

class IRCServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connections = []
        self.channels = {"General": []}
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
