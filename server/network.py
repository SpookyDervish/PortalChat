import socket, pickle, struct
from server.packet import Packet, PacketType


class Network:
    def __init__(self, server_ip: str):
        self.buffer_size = 2048
        self.port = 5555

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = server_ip
        self.addr = (self.server, self.port)
        self.connect()

    def send_image(self, image_path: str):
        """Send an image over the socket. The image is **required** to be in `.png` format."""
        # read image data
        with open(image_path, "rb") as f:
            image_data = f.read()

        self.client.setblocking(True)

        # Send length of data (4 bytes, big-endian unsigned int)
        self.client.sendall(struct.pack('>I', len(image_data)))

        # Send image data
        self.client.sendall(image_data)
    
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