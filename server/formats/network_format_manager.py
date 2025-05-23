import server.formats.network_format
from server.formats.raw_tcp import RawTcp
from server.formats.websockets_nf import Websocket

class NetworkFormatManager:
    network_formats: list[server.formats.network_format.NetworkFormat] = [RawTcp(), Websocket()]
    network_functions: server.formats.network_format.NetworkFormatFunctions = server.formats.network_format.NetworkFormatFunctions()
    running: bool = False

    def send_to_all_clients(self, packet: bytes) -> None:
        for network_format in self.network_formats:
            for client in network_format.network_connections:
                client.send(packet)

    def open(self):
        self.running = True
        self.network_functions.log("manager", "...")
        for network_format in self.network_formats:
            try:
                self.network_functions.log("manager", "test")
                network_format.network_functions = self.network_functions
                self.network_functions.log("manager", "set nf...")
                network_format.open()
                self.network_functions.log("manager", "nf open completed...")
            except Exception as e:
                self.network_functions.log("manager", str(e))

    def close(self):
        self.running = False
        for network_format in self.network_formats:
            network_format.close()
