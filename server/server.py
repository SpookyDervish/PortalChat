import socket
import pickle
import sys
from _thread import start_new_thread

from rich.traceback import install
from rich.console import Console
from server.packet import Packet, PacketType
from server.db import Database


console = Console()


class Server:
    def __init__(self, title: str, host: str = "0.0.0.0", log_level: int = 1):
        install(console=console)
        self.log_level = log_level
        self.BLOCKED_IPS = []

        self.server_info = {
            "title": title,
            "online": 0
        }

        self.log("Doing initial setup...", 1)
        self.clients = []
        self.host = host
        self.port = 5445

        self.log("Getting database...")
        self.db = Database()

        self.log("Creating socket...", 1)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.log("Attempting to bind socket..", level=1)
        try:
            self.sock.bind((self.host, self.port))
        except socket.error as e:
            self.log(f"Failed to bind socket! {e}", level=4)
            sys.exit(1)

        self.sock.listen()
        self.log("Server is listening and ready to receive connections!")
        self.log(f"IP: [bold green]{self.get_ip()}[/bold green]")

        self.log("Starting interactive terminal...", level=1)
        start_new_thread(self.interactive_terminal, ())

        self.log("Starting main server accept loop...", level=1)

        # main server loop
        while True:
            if self.sock.fileno() == -1: # the socket is closed
                break

            conn, addr = self.sock.accept()

            if addr[0] in self.BLOCKED_IPS:
                self.log(f"Ignored connection from blocked IP: {addr}", 3)
                conn.close()
                continue

            self.server_info["online"] += 1

            self.log(f"New connection! Address: {addr}")
            start_new_thread(self.handle_client, tuple([conn]))

    def interactive_terminal(self):
        while True:
            user_input = console.input("[bold green]>[/bold green] ")

            if user_input == "close":
                self.sock.close()
                break

    def handle_packet(self, packet: Packet):
        if packet.packet_type == PacketType.PING:
            return Packet(PacketType.PING, "HELLOOOo")
        elif packet.packet_type == PacketType.GET:
            if packet.data == "INFO":
                return Packet(PacketType.DATA, self.server_info)
            else:
                return Packet(PacketType.ERROR, "Invalid GET type!")
        else:
            return Packet(PacketType.ERROR, "Invalid packet type!")

    def handle_client(self, conn: socket.socket):
        self.log("Started new thread for client.", level=1)

        conn.send(pickle.dumps(Packet(PacketType.CONNECTION_STARTED, None)))

        while True:
            try:
                data = pickle.loads(conn.recv(2048))
                self.log(f"Receive: {data}")
                if not isinstance(data, Packet):
                    break

                if data.packet_type == PacketType.DISCONNECT:
                    break

                reply = self.handle_packet(data)

                self.log(f"Send   : {reply}")

                conn.sendall(pickle.dumps(reply))
            except (socket.error, EOFError) as e:
                self.log(f"A client created a socket error. The connection will be closed.\n\t- Client: {conn.getsockname()}\n\t- Error: {e}", 3)
                break

        self.log(f"Closing connection to {conn.getsockname()}.")
        conn.close()
        self.server_info["online"] -= 1

    def get_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        
        thing = s.getsockname()[0]

        s.close()

        return thing

    def log(self, message: str, level: int = 2):
        """
        Show a message to the console.

        # Levels:
            - 1: Debug, not useful to the average user.
            - 2: Info, use when you just want to show some information to the user that they might need.
            - 3: Warning, slightly important info
            - 4: Error, an error occured and the server can't continue running
        """
        if level < self.log_level:
            return
        
        message = str(message)
        
        final_message = ""

        if level == 1:
            final_message = f"[bold][[blue_violet]DEBUG[/blue_violet]][/bold]     {message}"
        elif level == 2:
            final_message = f"[bold][[spring_green2]INFO[/spring_green2]][/bold]      {message}"
        elif level == 3:
            final_message = f"[bold][[light_goldenrod1]WARNING[/light_goldenrod1]][/bold]   {message}"
        elif level == 4:
            final_message = f"[bold][[bright_red]ERROR[/bright_red]][/bold]     {message}"

        console.print(final_message, highlight=False)