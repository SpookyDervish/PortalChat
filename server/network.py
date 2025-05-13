import socket, pickle
from server.packet import Packet, PacketType


class Network:
    def __init__(self, server_ip: str):
        self.buffer_size = 2048
        self.port = 5555

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = server_ip
        self.addr = (self.server, self.port)
        self.user = self.connect()

        

    def get_client(self):
        return self.user
    
    def close(self):
        self.client.close()

    def recv(self) -> Packet:
        return pickle.loads(self.client.recv(self.buffer_size))

    def connect(self) -> Packet:
        self.client.connect(self.addr)
        return self.recv()
        
    def send(self, data) -> Packet:
        self.client.send(pickle.dumps(data))
        return self.recv()