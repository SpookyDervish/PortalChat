from __future__ import annotations
import socket
import threading

import msgpack
import sys, os
import traceback
from _thread import start_new_thread
from datetime import datetime
from time import sleep

from textual.widgets import RichLog
from rich.traceback import install
from rich.console import Console

from server.formats.network_format import NetworkConnection
from server.formats.network_format_manager import NetworkFormatManager
from server.packet import Packet, PacketType, to_bytes, to_packet
from server.db import Database

from api import command, Channel, Message

console = Console()


class Server:
    def nf_log(self, source: str, text: str):
        self.log(f"[bold][[blue_violet]{source}[/blue_violet]][/bold] {text}")

    def __init__(self, title: str, description: str = "", host: str = "", log_level: int = 1, rich_log: RichLog = None, interactive: bool = False):
        install(console=console)
        self.log_level = log_level
        self.rich_log = rich_log
        self.interactive = interactive
        self.BLOCKED_IPS = []

        self.server_info = {
            "title": title,
            "description": description,
            "online": 0
        }
        self.running = True

        self.log("Doing initial setup...", 1)
        #self.clients: list[socket.socket] = []
        #self.host = host
        #self.port = 5555

        self.ip = ""

        self.network_format_manager = NetworkFormatManager()
        self.network_format_manager.network_functions.on_client_open = self.handle_client
        self.network_format_manager.network_functions.log = self.nf_log

        # create needed folders
        NEEDED_FOLDERS = ["portal_server", "portal_server/user_icons"]
        for folder in NEEDED_FOLDERS:
            if not os.path.isdir(folder):
                os.mkdir(folder)

        self.log("Getting database...")
        self.db = Database(self, "portal_server/db.db")
    
    def __str__(self):
        return f"<{self.server_info['title']}>"

    def start(self):
        #self.log(str(self.network_format_manager))
        #exit(-1)

        self.ip = self.get_ip()

        self.network_format_manager.open()

        self.log("Server is listening and ready to receive connections!")
        self.log(f"IP: [bold green]{self.ip}[/bold green]")

        if self.interactive:
            self.log("Starting interactive terminal...", level=1)
            start_new_thread(self.interactive_terminal, ())


    def old_start(self):
        self.log("Creating socket...", 1)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.log("Attempting to bind socket..", level=1)
        try:
            self.sock.bind((self.host, self.port))
        except socket.error as e:
            self.log(f"Failed to bind socket! {e}", level=4)
            sys.exit(1)
        self.log(f"Server bound to: {self.sock.getsockname()}", 1)

        self.log(f"Server title is \"{self.server_info['title']}\"\n")

        self.sock.listen()

        self.log("Starting main server accept loop...", level=1)
        start_new_thread(self.main_loop, ())

        # keep main thread alive (is there a better way to do this?)
        try:
            while True: sleep(1)
        except KeyboardInterrupt:
            self.log("Interrupt received!", 2)
            self.stop()

    def main_loop(self):
        while self.running:
            if self.sock.fileno() == -1:  # the socket is closed
                self.running = False
                break

            try:
                conn, addr = self.sock.accept()
            except (ConnectionAbortedError, OSError, KeyboardInterrupt):  # socket was closed by server owner
                break

            if addr[0] in self.BLOCKED_IPS:
                self.log(f"Ignored connection from blocked IP: {addr}", 3)
                conn.close()
                continue

            start_new_thread(self.handle_client, tuple([conn]))

    def stop(self):
        self.log("[bold red blink]Server is shutting down![/]")
        self.running = False
        self.log("Closing socket...", 1)
        self.network_format_manager.close()
        #self.sock.close()
        self.log("Disconnecting db...", 1)
        self.db.close()

    def parse_command(self, message: str, channel_id: int, sender_info: dict):
        message = message.removeprefix("/")
        args = message.split()
        command_name = args.pop(0)

        # Construct a command context
        channel_ctx = Channel({"channel_id": channel_id, "name": self.db.get_channel_name_by_id(channel_id), "server_id": self.db.get_server_from_channel(channel_id)[0]}, self)
        message_ctx = Message({"content": message, "channel_id": channel_id, "channel_name": channel_ctx.name, "timestamp": datetime.now(), "server_id": channel_ctx.server_id}, self)
        context = command.CommandContext(
            channel_ctx,
            message_ctx
        )

        # TODO: handle invalid command names
        # run the command! :D
        try:
            command.command_registry[command_name](context, args)
            self.log(f"{sender_info['username']} ran the /{command_name} command!")
        except KeyError:
            self.log(f"{sender_info['username']} tried running an invalid command.")

    def send_message(self, message: str, channel_id: int, sender_conn: NetworkConnection, sender_info: dict):
        """Send a message to all users and save the message to the DB."""
        # if sender_info is None, that means that the message is a system msg
        if sender_info:
            sender_name: str = sender_info["username"]
            sender_uuid: str = sender_info["uuid"]

            if sender_uuid == "00000000-0000-0000-0000-000000000000":
                sender_conn.sendall(to_bytes(Packet(
                    PacketType.NOTIFICATION,
                    "Don't try to pretend to be a system user. :P"
                )))
                return False
        else:
            sender_name = "SYSTEM"
            sender_uuid = None

        if sender_uuid:
            if sender_name.strip() == "" or len(sender_name) > 25: # invalid username
                sender_conn.sendall(to_bytes(Packet(
                    PacketType.NOTIFICATION,
                    "You can't send messages because your username is invalid."
                )))
                return False

            if not self.db.user_exists(sender_uuid):
                self.log(f"Creating user because doesn't exist: {sender_uuid}")
                self.db.create_user(sender_name, sender_uuid)
                self.db.commit()

            current_username = self.db.get_user(sender_uuid)[1] 
            if current_username != sender_name: # user has changed their username since their last msg
                self.db.update_username(sender_uuid, sender_name)
                self.log(f"Updated username for {sender_uuid} from {current_username} to {sender_name}")

        # was it a command?
        if sender_uuid and message.startswith("/"):
            # parse it and don't show the message to other people in the server
            self.parse_command(message, channel_id, sender_info)
            return True

        # send the message to all users in the server
        self.log(f"@{sender_name} said \"{message}\" in channel ID [cyan]{channel_id}[/cyan].")
        if sender_uuid:
            self.db.create_message_in_channel(channel_id, sender_uuid, sender_name, message)
        else:
            self.db.create_message_in_channel(channel_id, "00000000-0000-0000-0000-000000000000", "SYSTEM", message)
        self.log("Saving DB...")
        self.db.commit()

        packet = Packet(
                PacketType.MESSAGE_RECV,
                {"message": message, "sender_name": sender_name, "timestamp": datetime.now(), "channel_id": channel_id, "channel_name": self.db.get_channel_name_by_id(channel_id), "server_id": self.db.get_server_from_channel(channel_id)[0], "server_ip": self.ip}
            )

        self.network_format_manager.send_to_all_clients(to_bytes(packet))
        #for user in:
            #if user == sender_conn: continue
            #self.log(f"Sending packet to {user}: {packet}", 2)
            #user.send()

        return True

    def interactive_terminal(self):
        while True:
            try:
                user_input = console.input("[bold green]>[/bold green] ")

                if user_input == "close":
                    self.stop()
                    break
            except (EOFError, KeyboardInterrupt): break

    def handle_packet(self, packet: Packet, conn: NetworkConnection):
        reply = None
        
        try:
            if packet.packet_type == PacketType.NONE:
                reply = None
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
                        reply = Packet(PacketType.DATA, {"data": {"messages": messages, "channel_name": self.db.get_channel_name_by_id(channel_id)}, "type": "SERVER_MSGS"})
                elif packet.data["type"] == "MEMBERS":
                    channel_id = packet.data["channel_id"]
                    server = self.db.get_server_from_channel(channel_id)

                    if not server:
                        return Packet(PacketType.ERROR, "Channel does not exist!", tag=packet.tag)
                    
                    server_id = server[0]
                    
                    channel = self.db.get_channel(server_id, channel_id)

                    reply = Packet(PacketType.DATA, {"data": self.db.get_roles_with_users_in_server(server_id), "type": "SERVER_MEMBERS"})
                    
                else:
                    reply = Packet(PacketType.ERROR, "Invalid GET type!")
            elif packet.packet_type == PacketType.MESSAGE_SEND:
                msg = packet.data["message"].strip()

                if msg == "":
                    reply = Packet(PacketType.ERROR, "Can't send an empty message.")

                channel_id = packet.data["channel_id"] # TODO: check if the user has permission to send to that channel
                
                user_name = packet.data["username"]
                was_sent = self.send_message(msg, channel_id, conn, {"username": user_name, "uuid": packet.data["uuid"]})
                reply = Packet(
                        PacketType.MESSAGE_RECV,
                        {"message": msg, "sender_name": f"{user_name}{not was_sent and ' [dim red](NOT SENT)[/] ' or ''}", "timestamp": datetime.now(), "channel_id": channel_id, "channel_name": self.db.get_channel_name_by_id(channel_id), "server_ip": self.ip}
                    )
            else:
                reply = Packet(PacketType.ERROR, "Invalid packet type!")
        except Exception:
            self.log(f"Error while handling packet:\n[bold red]{traceback.format_exc()}[/bold red]", 3)
            reply = Packet(PacketType.ERROR, "Internal Server Error")

        if reply:
            reply.tag = packet.tag
        return reply

    def handle_client(self, conn: NetworkConnection) -> bool:
        self.log(f"New connection! Address: {conn.addr}")

        if conn.addr[0] in self.BLOCKED_IPS:
            self.log(f"Ignored connection from blocked IP: {conn.addr}", 3)
            conn.close()
            return False

        def client_loop():
            self.server_info["online"] += 1

            self.log("Started new thread for client.", level=1)

            conn.send(to_bytes(Packet(PacketType.CONNECTION_STARTED, None)))

            while self.network_format_manager.running:
                try:
                    try:
                        recv_data = conn.recv()
                        data = to_packet(recv_data)[0]
                    except (msgpack.ExtraData, ValueError):  # idk why it does this, but it still works lmao
                        pass
                    except (msgpack.FormatError, msgpack.StackError, msgpack.UnpackValueError) as e:
                        self.log(
                            f"CLIENT ATTEMPTED TO SEND NON-PACKET DATA:\n\t- Data: \"{data}\"\n\t- Traceback: [bold red]{traceback.format_exc()}",
                            3)
                        conn.close()
                        break

                    self.log(f"Receive: {data}", 1)

                    if data.packet_type == PacketType.DISCONNECT:
                        self.log("Client disconnected via packet.", 1)
                        break

                    reply = self.handle_packet(data, conn)

                    self.log(f"Send   : {reply}", 1)

                    if reply != None:
                        conn.sendall(to_bytes(reply))
                except (socket.error, EOFError) as e:
                    self.log(
                        f"A client created a socket error. The connection will be closed.\n\t- Client: {conn.getsockname()}\n\t- Error: [bold red]{traceback.format_exc()}",
                        3)
                    conn.close()
                    break

            self.log(f"Closing connection to {conn.getsockname()}.")
            conn.close()
            self.server_info["online"] -= 1

        threading.Thread(target=client_loop).start()

        return True

    def get_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        
        thing = s.getsockname()[0]

        s.close()

        return thing
    
    def recv_all(self, length: int):
        data = b''
        while len(data) < length:
            more = self.sock.recv(length - len(data))
            if not more:
                raise EOFError("Socket closed before we received all data")
            data += more
        return data

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
        
        #message = str(message)
        
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
            if self.rich_log:
                self.rich_log.write(final_message)
            else:
                console.print(final_message, highlight=False)
        except:
            if self.rich_log:
                self.rich_log.write(final_message)
            else:
                console.print(final_message, highlight=False, markup=False)
            