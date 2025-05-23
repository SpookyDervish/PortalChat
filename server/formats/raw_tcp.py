from __future__ import annotations

import socket
import threading
from typing import Any

import server.formats.network_format

class RawTcpConnection(server.formats.network_format.NetworkConnection):
    __socket: socket.socket = None
    __host: RawTcp = None

    def sendall(self, message: bytes):
        self.__socket.sendall(message)
        pass

    def send(self, message: bytes):
        self.__socket.send(message)
        pass

    def recv(self) -> bytes:
        return self.__socket.recv(2048)

    def close(self) -> None:
        if self.__socket.fileno() == -1:
            self.__socket.close()

        self.__host.server_sockets.remove(self)

    def __init__(self, raw_tcp: RawTcp, conn: socket.socket, addr: Any):
        self.__host = raw_tcp
        self.__socket = conn
        self.addr = addr
        super().__init__()


class RawTcp(server.formats.network_format.NetworkFormat):
    __server_thread: threading.Thread = None
    __server_server: socket.socket = None
    server_sockets: list[RawTcpConnection] = []

    def server(self):
        while self.running:
            if self.__server_server.fileno() == -1:  # the socket is closed
                self.running = False
                break

            try:
                self.network_functions.log("Raw TCP", "Waiting for connection...")
                conn, addr = self.__server_server.accept()
                self.network_functions.log("Raw TCP", "Accepting connection...")
            except (ConnectionAbortedError, OSError, KeyboardInterrupt):  # socket was closed by server owner
                break

            new_raw_tcp_connection = RawTcpConnection(self, conn, addr)

            if self.network_functions.on_client_open(new_raw_tcp_connection):
                self.network_functions.log("Raw TCP", "Connection authorised!")
                self.server_sockets.append(new_raw_tcp_connection)
            else:
                self.network_functions.log("Raw TCP", "Server rejected connection.")

    def open(self) -> None:
        if self.running: return

        self.running = True
        self.__server_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server_server.bind(("", 5555))
        self.__server_server.listen()
        self.__server_thread = threading.Thread(target=self.server)
        self.__server_thread.start()
        pass

    def close(self) -> None:
        if not self.running: return

        self.running = False
        self.__server_server.close()
        self.__server_thread.join()
        pass

    def __init__(self):
        super().__init__()