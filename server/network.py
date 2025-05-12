import socket, pickle
from server.packet import Packet, PacketType


class Network:
    def __init__(self, server_ip: str):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = server_ip
        self.port = 5555
        self.addr = (self.server, self.port)
        self.user = self.connect()

    def get_client(self):
        return self.user

    def connect(self) -> Packet:
        self.client.connect(self.addr)
        return pickle.loads(self.client.recv(2048))
        
    def send(self, data) -> Packet:
        self.client.send(pickle.dumps(data))
        return pickle.loads(self.client.recv(2048))