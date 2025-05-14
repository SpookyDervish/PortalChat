import socket, pickle, time
from server.packet import Packet, PacketType


class Network:
    def __init__(self, server_ip: str):
        self.buffer_size = 2048
        self.port = 5555

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = server_ip
        self.addr = (self.server, self.port)
        self.connect()
    
    def close(self):
        self.client.close()

    def recv(self, blocking: bool = False) -> Packet:
        self.client.setblocking(blocking)
        try:
            response = self.client.recv(self.buffer_size)
        except (BlockingIOError, socket.error):
            return None

        return pickle.loads(response)

    def connect(self):
        self.client.connect(self.addr)
        
    def send(self, data) -> Packet:

        self.client.send(pickle.dumps(data))
        return self.recv(True)