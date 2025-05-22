from abc import abstractmethod
from typing import Callable, Any


class NetworkConnection:
    addr: Any = None

    @abstractmethod
    def sendall(self, message: bytes):
        pass

    @abstractmethod
    def send(self, message: bytes):
        pass

    @abstractmethod
    def recv(self) -> bytes:
        pass

    @abstractmethod
    def close(self) -> None:
        pass

class NetworkFormatFunctions:
    on_client_open: Callable[[NetworkConnection], bool] = None
    log: Callable[[str, str], None]

class NetworkFormat:
    """A generic NetworkFormat class.
    NetworkFormat is to be the network server of a particular transport protocol.

    :parameter network_functions: The NetworkFormatFunctions instance.
    :parameter network_connections: The NetworkConnections instances that are being managed by this NetworkFormat instance.
    :parameter running: The state of the server."""
    network_functions: NetworkFormatFunctions = None
    network_connections: list[NetworkConnection] = []
    running: bool = False

    @abstractmethod
    def open(self) -> None:
        """Opens a NetworkFormat server.
        The state of the server by the derived class.
        The functions set in network_functions are to be called by the derived class on the conditions described.
        """
        if (self.network_functions is None
         or self.network_functions.on_client_open is None
         or self.network_functions.log is None):
            raise ValueError("network_functions must be filled.")
        pass

    @abstractmethod
    def close(self) -> None:
        """Closes a NetworkFormat server.
        On close, all clients are to immediately close as soon as possible."""
        pass