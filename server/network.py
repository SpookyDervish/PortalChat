import socket, struct
from server.packet import Packet, PacketType, to_packet, to_bytes


class Network:
    def __init__(self, server_ip: str):
        self.buffer_size = 2048 * 4
        self.port = 5555

        self.TIMEOUT = 1 # if a socket exceeds 1 second latency on a GOD DAMN LAN CONNECTION, then the packet must not have been received lol

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

    def recv(self, blocking: bool = False) -> list[Packet]:
        self.client.setblocking(blocking)

        if blocking:
            self.client.settimeout(self.TIMEOUT)

        try:
            response = self.client.recv(self.buffer_size)
        except (BlockingIOError, socket.error):
            return None

        return to_packet(response)

    def connect(self):
        self.client.connect(self.addr)
        
    def send(self, data, blocking: bool = True) -> Packet:

        self.client.send(to_bytes(data))
        return self.recv(blocking)