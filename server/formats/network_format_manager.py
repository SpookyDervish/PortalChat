from server.formats.network_format import NetworkFormat, NetworkFormatFunctions
from server.formats.raw_tcp import RawTcp


class NetworkFormatManager:
    network_formats: list[NetworkFormat] = [RawTcp()]
    network_functions: NetworkFormatFunctions = NetworkFormatFunctions()
    running: bool = False

    def send_to_all_clients(self, packet: bytes) -> None:
        for network_format in self.network_formats:
            for client in network_format.network_connections:
                client.send(packet)

    def open(self):
        self.running = True
        self.network_functions.log("manager", "...")
        for network_format in self.network_formats:
            self.network_functions.log("manager", "test")
            network_format.network_functions = self.network_functions
            network_format.open()

    def close(self):
        self.running = False
        for network_format in self.network_formats:
            network_format.close()
