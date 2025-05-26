from __future__ import annotations

import threading
import websockets.sync.server
import server.formats.network_format

class WebsocketConnection(server.formats.network_format.NetworkConnection):
    __socket: websockets.sync.server.ServerConnection
    __host: Websocket
    websocketSemaphore = threading.BoundedSemaphore()

    def sendall(self, message: bytes):
        self.send(message)
        pass

    def send(self, message: bytes):
        self.__socket.send(message)
        pass

    def recv(self) -> bytes:
        return self.__socket.recv()

    def close(self) -> None:
        if self.__socket.close_code is not None:
            self.__socket.close()

        self.__host.network_connections.remove(self)
        self.websocketSemaphore.release()
        pass

    def __init__(self, host: Websocket, connection: websockets.sync.server.ServerConnection):
        self.__host = host
        self.__socket = connection
        self.addr = connection.local_address
        super().__init__()
        pass

class Websocket(server.formats.network_format.NetworkFormat):
    __server_thread: threading.Thread = None
    __server_socket: websockets.sync.server.Server = None

    def server(self):
        def handler(server_connection: websockets.sync.server.ServerConnection) -> None:
            try:
                self.network_functions.log("Websocket", str(server_connection))
                self.network_functions.log("Websocket", "New connection - checking...")
                new_network_connection = WebsocketConnection(self, server_connection)

                if self.network_functions.on_client_open(new_network_connection):
                    self.network_functions.log("Websocket", "Connection authorised!")
                    self.network_connections.append(new_network_connection)

                    new_network_connection.websocketSemaphore.acquire()
                    new_network_connection.websocketSemaphore.acquire()
                    self.network_functions.log("Websocket", "Ended.")
                else:
                    self.network_functions.log("Websocket", "Server rejected connection.")
            except Exception as e:
                self.network_functions.log("Websocket", "[yellow]Exception on handling...[/yellow]")
                self.network_functions.log("Websocket", str(e))

        try:
            self.__server_socket = websockets.sync.server.serve(handler, host="", port=5551)
            self.network_functions.log("Websocket", "Handing off control to websocket server...")
            self.__server_socket.serve_forever()
            self.network_functions.log("Websocket", "Houston?")
        except Exception as e:
            self.network_functions.log("Websocket", str(e))

    def open(self) -> None:
        super().open()
        self.__server_thread = threading.Thread(target=self.server)
        self.network_functions.log("Websocket", "Starting websocket server thread...")
        self.__server_thread.start()
        pass

    def close(self) -> None:
        super().close()

        self.__server_socket.shutdown()

        pass

    def __init__(self):
        super().__init__()