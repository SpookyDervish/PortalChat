import socket, pickle
from server.packet import Packet, PacketType


class Network:
    def __init__(self, server_ip: str):
        self.buffer_size = 2048
        self.port = 5555
        self.timeout = 5

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(self.timeout)
        self.client.setblocking(0)
        self.server = server_ip
        self.addr = (self.server, self.port)
        self.user = self.connect()

        

    def get_client(self):
        return self.user
    
    def close(self):
        self.client.close()

    def recv(self) -> Packet:
        response = self.client.recv(self.buffer_size)
        if not response: return None
        return pickle.loads(response)

    def connect(self) -> Packet:
        self.client.connect(self.addr)
        return self.recv()
        
    def send(self, data) -> Packet:
        self.client.send(pickle.dumps(data))
        return self.recv()