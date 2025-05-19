from textual.app import App, ComposeResult
from textual.widgets import Tree, Label, Rule
from textual.css.query import NoMatches
from textual import work
from queue import Queue

import uuid
import os
import configparser
import playsound

from ui.config import DEFAULT_CONFIG, conf_get
from ui.widgets.update_screen import UpdateScreen
from ui.widgets.sidebar import ServerList, ChannelList, MemberList
from ui.widgets.welcome import Welcome
from ui.widgets.chat import Chat, Message
from ui.widgets.message_box import ChatArea
from ui.widgets.server_overview import ServerOverview

from desktop_notifier import DesktopNotifier, Icon

from server.network import Network
from server.packet import Packet, PacketType


class Portal(App):
    DEFAULT_CSS = """
    .start-rule {
        color: $background-lighten-1;
    }
    """
    
    ENABLE_COMMAND_PALETTE = False

    def compose(self) -> ComposeResult:
        yield ServerList(id="sidebar")
        yield ChannelList()
        yield Chat()
        yield Welcome()
        yield ChatArea()
        yield MemberList()

    def action_quit(self):
        self.is_open = False
        if self.n:
            self.n.client.close()
        if self.ping_loop_worker:
            self.ping_loop_worker.cancel()
            self.ping_loop_worker = None
        if self.packet_handler_worker:
            self.packet_handler_worker.cancel()
            self.packet_queue.put(Packet(PacketType.STOP))
            self.packet_handler_worker = None
        return super().action_quit()

    def init_settings_file(self):
        for key in DEFAULT_CONFIG:
            self.config[key] = DEFAULT_CONFIG[key]
        with open('user_settings.ini', "w") as config_file:
            self.config.write(config_file)


    def on_mount(self):
        # generate unique user id
        if not os.path.isfile("my_id.txt"):
            with open("my_id.txt", "w") as f:
                f.write(str(uuid.uuid4()))

        # get unique user id
        with open("my_id.txt") as f:
            self.user_id = f.read()

        self.config = configparser.ConfigParser()
        if not os.path.isfile('user_settings.ini'):
            self.init_settings_file()
        self.config.read("user_settings.ini")
        self.theme = conf_get(self.config, "Appearance", "theme")

        self.desktop_notifier = DesktopNotifier(app_name="Portal")

        self.is_open = True
        self.n = None
        self.channel_id = None
        self.opened_server = None
        self.query_one(Chat).styles.display = "none"
        self.query_one(ChannelList).styles.display = "none"
        self.query_one(ChatArea).display = "none"
        self.query_one(MemberList).display = "none"
        self.ping_loop_worker = None
        self.packet_handler_worker = None
        self.packet_queue: Queue[Packet] = Queue()
        self.notify("Portal is [bold]EXTREMELY[/bold] buggy at the moment, watch out! I'm currently migrating it to a queue system, and so your app may freeze when doing certain things, know I am working to fix this!", title="Watch out!", severity="warning", timeout=10)
        self.app.push_screen(UpdateScreen())

    def on_tree_node_selected(self, event: Tree.NodeSelected):
        if self.n is None: return
        chat = self.query_one(Chat)
        chat_area = self.query_one(ChatArea)

        if event.node.tree.id != "channels": return

        if event.node == event.node.tree.root or event.node.data == None:
            self.packet_queue.put(self.n.send(Packet(PacketType.GET, {"type": "INFO"}, tag="server-overview")))
            chat.display = "none"
            chat_area.display = 'none'
        else:
            chat.display = "block"
            chat_area.display = 'block'
            try:
                overview = self.query_one(ServerOverview)
                overview.remove()
            except:
                pass

            data = event.node.data
            self.channel_id = data

            # Get messages in the selected channel
            self.packet_queue.put(self.n.send(Packet(PacketType.GET, {"type": "MESSAGES", "channel_id": self.channel_id}, tag="servr-msgs")))

            # Update member list
            self.packet_queue.put(self.n.send(Packet(PacketType.GET, {"type": "MEMBERS", "channel_id": self.channel_id}, tag="servr-members")))
        
        

    @work
    async def send_message(self, message: str):
        self.n.send(Packet(PacketType.MESSAGE_SEND, {"message": message, "channel_id": self.channel_id, "username": conf_get(self.config, "MyAccount", "username"), "uuid": self.user_id}))
        #self.packet_queue.put(response)

    @work
    async def mount_msgs(self, chat, data, banner: bool = False):
        if banner:
            await chat.mount(Label(f"[b][u]Welcome![/u][/b]\n[dim]This is the start of the #{data['channel_name']} channel.[/dim]\n[dim]Portal has only [bold]just started development[/bold], so watch out for bugs![/dim]"))
            await chat.mount(Rule(classes="start-rule"))

        for msg in data["messages"]:
            # the message id is message[0]
            # the message contents is message[1]
            # the timestamp (in string format) is message[2]
            # the sender name is message [3]
            await chat.mount(Message(
                msg[1],
                msg[3],
                msg[2]
            ))

    @work
    async def update_welcome(self, server_info):
        try:
            self.query_one(ServerOverview).remove()
        except NoMatches:
            pass

        self.mount(ServerOverview(server_info), after=self.query_one(ChannelList))

    @work
    async def send_notification(self, title: str, message: str):
        await self.desktop_notifier.send(title, message=message)

    @work(thread=True)
    def packet_handler(self):
        chat = self.query_one(Chat)
        channel_list = self.query_one(ChannelList)
        member_list = self.query_one(MemberList)

        while self.is_open:
            packet = self.packet_queue.get()

            if packet == None: continue

            self.app.log(f"Got packet from queue: {packet}")
            if packet.packet_type == PacketType.STOP:
                self.app.log("Stopping packet handler...")
                break
            elif packet.packet_type == PacketType.MESSAGE_RECV:
                self.app.log("Calling mount_msgs from the main thread...")

                if packet.data["channel_id"] != self.channel_id:
                    if bool(int(conf_get(self.config, "Notifications", "notification-sound"))):
                        playsound.playsound(os.path.abspath("assets/sounds/notification.mp3"), False)
                    if bool(int(conf_get(self.config, "Notifications", "desktop-notifications"))):
                        self.send_notification(
                            f"Message in #{packet.data['channel_name']} from @{packet.data['sender_name']}",
                            packet.data["message"]
                        )
                else:
                    self.call_from_thread(self.mount_msgs, chat, {
                        "messages": [(
                            None, # not needed atm
                            packet.data["message"],
                            packet.data["timestamp"],
                            packet.data["sender_name"]
                        )],
                        "channel_name": packet.data["channel_name"]
                    })
                self.app.log("Done with msgs!")
            elif packet.packet_type == PacketType.DATA:
                if packet.data["type"] == "SERVER_CHANNELS":
                    self.app.log("Updating channel list...")

                    channel_list.clear()
                    for channel in packet.data["data"]:
                        channel_id = channel[0]
                        channel_name = channel[1]

                        channel_list.root.add_leaf(channel_name, data=channel_id)
                    channel_list.root.expand_all()

                    self.app.log("Done updating channel list!")
                elif packet.data["type"] == "SERVER_MSGS":
                    
                    data = packet.data["data"]
                    # delete other messages
                    self.app.log("Clearing previous msg history...")
                    chat.remove_children()

                    self.app.log("Calling mount_msgs from a thread to update entire message history...")
                    # add new messages
                    self.call_from_thread(self.mount_msgs, chat, data, banner=True)
                    self.app.log("Done redrawing entire message history!")
                elif packet.data["type"] == "SERVER_MEMBERS":
                    member_list.clear()
                    for role in packet.data["data"]:
                        role_name = role[0]
                        members_with_role = role[1]

                        if role_name == "DefaultPerms":
                            for member in members_with_role:
                                member_list.root.add_leaf(member)
                        else:
                            role_node = member_list.root.add(role_name)
                            for member in members_with_role:
                                role_node.add_leaf(member)
                    member_list.root.expand_all()
                elif packet.tag == "server-overview":
                    self.app.log("Updating welcome...")
                    self.call_from_thread(self.update_welcome, packet.data["data"])
                    self.app.log("Done updating welcome!")
                else:
                    self.notify(f"Unhandled DATA packet: {packet}", title="Warning!", severity="warning", markup=False, timeout=10)
            elif packet.packet_type == PacketType.PING:
                self.app.log("Ignoring ping packet...")
                pass # ignore ping packets
            elif packet.packet_type == PacketType.CONNECTION_STARTED:
                self.app.log("Ignoring connection packet...")
                pass # ignore connection started packets
            elif packet.packet_type == PacketType.NOTIFICATION:
                self.log(packet.data)
                self.notify(packet.data)
            else:
                self.notify(f"Unhandled packet: {packet}", title="Warning!", severity="warning", markup=False, timeout=10)

    @work(thread=True)
    def ping_loop(self):
        try:
            while self.is_open:
                response = self.n.recv()
                if response != None:
                    self.packet_queue.put(response)
        except Exception: # server was closed
            server_list = self.query_one(ServerList)
            for button in server_list.query_one("#icons").children:
                if "server-btn" in button.classes:
                    if button.info[2] == self.n.client.getpeername()[0]: # if the button refers to the server that just closed, then delete the button
                        button.remove()

            self.notify(message="The host of the server shut down the server.", title="Woops!", severity="warning", timeout=10)
            self.open_server(None)

    def open_server(self, server_info):
        if self.ping_loop_worker:
            self.ping_loop_worker.cancel()
            self.ping_loop_worker = None
        if self.packet_handler_worker:
            self.packet_handler_worker.cancel()
            self.packet_handler_worker = None
        if self.n:
            self.n.close()
            self.n = None

        chat = self.query_one(Chat) # chat history
        chat_area = self.query_one(ChatArea) # message box
        channel_list = self.query_one(ChannelList)
        welcome = self.query_one(Welcome)
        member_list = self.query_one(MemberList)

        if server_info == None: # go back to welcome screen
            welcome.display = "block"
            chat.display = "none"
            chat_area.display = 'none'
            channel_list.display = "none"
            member_list.display = "none"

            try:
                overview = self.query_one(ServerOverview)
                overview.remove()
            except:
                pass

            return

        try:
            self.n = Network(server_info[2]) # start a connection to the server
        except ConnectionRefusedError: # the server isn't online
            self.notify("That server isn't online at the moment.", title="Sorry!", severity="warning")
            return
        

        chat.styles.display = "block"
        channel_list.styles.display = "block"
        channel_list.root.set_label("🌀 [bold red]" + server_info[0] + "[/]")
        welcome.styles.display = "none"
        member_list.display = "block"

        channel_list.select_node(channel_list.root)
        self.ping_loop_worker = self.ping_loop()
        self.packet_handler_worker = self.packet_handler()
        self.packet_queue.put(self.n.send(Packet(PacketType.GET, {"type": "CHANNELS"})))