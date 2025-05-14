import socket
import pickle
import sys
import traceback
from _thread import start_new_thread
from datetime import datetime

from rich.traceback import install
from rich.console import Console
from server.packet import Packet, PacketType
from server.db import Database


console = Console()


class Server:
    def __init__(self, title: str, description: str = "", host: str = "", log_level: int = 1):
        install(console=console)
        self.log_level = log_level
        self.BLOCKED_IPS = []

        self.server_info = {
            "title": title,
            "description": description,
            "online": 0
        }

        self.log("Doing initial setup...", 1)
        self.clients: list[socket.socket] = []
        self.host = host
        self.port = 5555

        self.log("Getting database...")
        self.db = Database(self)

        self.log("Creating socket...", 1)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.log("Attempting to bind socket..", level=1)
        try:
            self.sock.bind((self.host, self.port))
        except socket.error as e:
            self.log(f"Failed to bind socket! {e}", level=4)
            sys.exit(1)
        self.log(f"Server bound to: {self.sock.getsockname()}", 1)

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
            self.clients.append(conn)

            self.log(f"New connection! Address: {addr}")
            start_new_thread(self.handle_client, tuple([conn]))

    def send_message(self, message: str, channel_id: int, sender_conn: socket.socket = None, sender_name: str = None):
        """Send a message to all users and save the message to the DB.

        Args:
            message (str): The string contents of the message
            sender_name (str, optional): What is the name of the user who sent the message? Defaults to a system message with no sender.
        """
        self.log(f"@{sender_name} said \"{message}\" in channel ID [cyan]{channel_id}[/cyan].")
        self.db.create_message_in_channel(channel_id, self.db.get_user_by_name(sender_name)[0], message)
        self.log("Saving DB...")
        self.db.commit()

        packet = Packet(
                PacketType.MESSAGE_RECV,
                {"message": message, "sender_name": sender_name, "timestamp": datetime.now(), "channel_id": channel_id, "channel_name": self.db.get_channel_name_by_id(channel_id)}
            )

        for user in self.clients:
            #if user == sender_conn: continue

            self.log(f"Sending packet to {user}: {packet}", 1)

            user.send(pickle.dumps(packet))

    def interactive_terminal(self):
        while True:
            user_input = console.input("[bold green]>[/bold green] ")

            if user_input == "close":
                self.sock.close()
                break

    def handle_packet(self, packet: Packet, conn: socket.socket):
        reply = None

        try:
            if packet.packet_type == PacketType.WAIT:
                reply = None
            elif packet.packet_type == PacketType.PING:
                reply = Packet(PacketType.PING)
            elif packet.packet_type == PacketType.GET:
                if packet.data["type"] == "INFO":
                    reply = Packet(PacketType.DATA, {"data": self.server_info, "type": "SERVER_INFO"})
                elif packet.data["type"] == "CHANNELS": # TODO: create private channels
                    channels = self.db.get_channels_in_server(self.db.get_server_by_name(self.server_info["title"])[0])
                    reply = Packet(PacketType.DATA, {"data": channels, "type": "SERVER_CHANNELS"})
                elif packet.data["type"] == "MESSAGES": # TODO: don't let the user see message history of private channels
                    channel_id = packet.data["channel_id"]
                    messages = self.db.get_messages_in_channel(channel_id)
                    server = self.db.get_server_from_channel(channel_id)

                    if messages == None and server == None:
                        reply = Packet(PacketType.ERROR, "Channel doesn't exist!")
                    else:
                        reply = Packet(PacketType.DATA, {"data": {"messages": messages, "channel_name": server[1]}, "type": "SERVER_MSGS"})
                else:
                    reply = Packet(PacketType.ERROR, "Invalid GET type!")
            elif packet.packet_type == PacketType.MESSAGE_SEND:
                msg = packet.data["message"].strip()

                if msg == "":
                    reply = Packet(PacketType.ERROR, "Can't send an empty message.")

                channel_id = packet.data["channel_id"] # TODO: check if the user has permission to send to that channel
                
                self.send_message(msg, channel_id, conn, "user")
                reply = Packet(
                    PacketType.MESSAGE_RECV,
                    {"message": msg, "sender_name": "user", "timestamp": datetime.now(), "channel_id": channel_id, "channel_name": self.db.get_channel_name_by_id(channel_id)}
                )
            else:
                reply = Packet(PacketType.ERROR, "Invalid packet type!")
        except Exception:
            self.log(f"Error while handling packet:\n[bold red]{traceback.format_exc()}[/bold red]", 3)
            reply = Packet(PacketType.ERROR, "Internal Server Error")

        if reply:
            reply.tag = packet.tag
        return reply

    def handle_client(self, conn: socket.socket):
        self.log("Started new thread for client.", level=1)

        conn.send(pickle.dumps(Packet(PacketType.CONNECTION_STARTED, None)))

        while True:
            try:
                data = pickle.loads(conn.recv(2048))
                if not isinstance(data, Packet):
                    break
                if data.packet_type != PacketType.PING:
                    self.log(f"Receive: {data}", 1)

                if data.packet_type == PacketType.DISCONNECT:
                    break

                reply = self.handle_packet(data, conn)

                if reply != None:
                    if reply.packet_type != PacketType.PING:
                        self.log(f"Send   : {reply}", 1)

                    conn.sendall(pickle.dumps(reply))
            except (socket.error, EOFError) as e:
                self.log(f"A client created a socket error. The connection will be closed.\n\t- Client: {conn.getsockname()}\n\t- Error: {e}", 3)
                break

        self.log(f"Closing connection to {conn.getsockname()}.")
        conn.close()
        self.clients.remove(conn)
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

        try:
            console.print(final_message, highlight=False)
        except:
            console.print(final_message, highlight=False, markup=False)