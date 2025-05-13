from textual.app import App, ComposeResult
from textual.widgets import Tree, Label, Rule
from textual.css.query import NoMatches
from textual import work
from queue import Queue
import datetime
import time

from ui.widgets.sidebar import ServerList, ChannelList
from ui.widgets.welcome import Welcome
from ui.widgets.chat import Chat, Message
from ui.widgets.message_box import ChatArea
from ui.widgets.server_overview import ServerOverview

from server.network import Network
from server.packet import Packet, PacketType

class Portal(App):
    DEFAULT_CSS = """
    .start-rule {
        color: $background-lighten-1;
    }
    """
    

    def compose(self) -> ComposeResult:
        yield ServerList(id="sidebar")
        yield ChannelList()
        yield Chat()
        yield Welcome()
        yield ChatArea()

    def action_quit(self):
        self.is_open = False
        if self.n:
            self.n.client.close()
        if self.ping_loop_worker:
            self.ping_loop_worker.cancel()
            self.ping_loop_worker = None
        if self.packet_handler_worker:
            self.packet_handler_worker.cancel()
            self.packet_handler_worker = None
        return super().action_quit()

    def on_mount(self):
        self.is_open = True
        self.n = None
        self.channel_id = None
        self.opened_server = None
        self.query_one(Chat).styles.display = "none"
        self.query_one(ChannelList).styles.display = "none"
        self.query_one(ChatArea).display = "none"
        self.ping_loop_worker = None
        self.packet_handler_worker = None
        self.packet_queue: Queue[Packet] = Queue()

    def on_tree_node_selected(self, event: Tree.NodeSelected):
        if self.n is None: return
        chat = self.query_one(Chat)
        chat_area = self.query_one(ChatArea)

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

            self.packet_queue.put(self.n.send(Packet(PacketType.GET, {"type": "MESSAGES", "channel_id": self.channel_id}, tag="servr-msgs")))
        
        

    @work
    async def send_message(self, message: str):
        response = self.n.send(Packet(PacketType.MESSAGE_SEND, {"message": message, "channel_id": self.channel_id}))
        self.packet_queue.put(response)

    def mount_msgs(self, chat, data, banner: bool = False):
        if banner:
            chat.mount(Label(f"[b][u]Welcome![/u][/b]\n[dim]This is the start of the #{data['channel_name']} channel.[/dim]\n[dim]Portal has only [bold]just started development[/bold], so watch out for bugs![/dim]"))
            chat.mount(Rule(classes="start-rule"))

        for msg in data["messages"]:
            # the message id is message[0]
            # the message contents is message[1]
            # the timestamp (in string format) is message[2]
            # the sender name is message [3]
            chat.mount(Message(
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

    @work(thread=True)
    def packet_handler(self):
        chat = self.query_one(Chat)
        channel_list = self.query_one(ChannelList)

        while self.is_open:
            packet = self.packet_queue.get()
            if packet.packet_type == PacketType.MESSAGE_RECV:
                self.call_from_thread(self.mount_msgs(chat, {
                    "messages": [(
                        None, # not needed atm
                        packet.data["message"],
                        packet.data["timestamp"],
                        packet.data["sender_name"]
                    )],
                    "channel_name": None
                }))
            elif packet.packet_type == PacketType.DATA:
                if packet.data["type"] == "SERVER_CHANNELS":
                    channel_list.clear()
                    for channel in packet.data["data"]:
                        channel_id = channel[0]
                        channel_name = channel[1]

                        channel_list.root.add_leaf(channel_name, data=channel_id)
                    channel_list.root.expand_all()
                elif packet.data["type"] == "SERVER_MSGS":
                    data = packet.data["data"]
                    # delete other messages
                    chat.remove_children()

                    # add new messages
                    self.call_from_thread(self.mount_msgs(chat, data, banner=True))
                elif packet.tag == "server-overview":
                    self.update_welcome(packet.data["data"])
            elif packet.packet_type == PacketType.PING:
                pass # ignore ping packets
            else:
                self.notify(f"Unhandled packet: {packet}", title="Warning!", severity="warning")

    @work(thread=True)
    def ping_loop(self):
        try:
            while self.is_open:
                #self.n.client.recv(self.n.buffer_size)
                """response = self.n.send(Packet(PacketType.WAIT))
                self.packet_queue.put(response)
                sleep(0.1)"""

                self.packet_queue.put(self.n.recv())
                #self.packet_queue.put(Packet(PacketType.MESSAGE_RECV, {"message": "test", "timestamp": datetime.datetime.now(), "sender_name": "user"}), block=False)
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

        chat = self.query_one(Chat)
        channel_list = self.query_one(ChannelList)
        welcome = self.query_one(Welcome)

        if server_info == None: # go back to welcome screen
            welcome.display = "block"
            chat.display = "none"
            channel_list.display = "none"

            try:
                overview = self.query_one(ServerOverview)
                overview.remove()
            except:
                pass

            return

        self.n = Network(server_info[2]) # start a connection to the server
        self.packet_queue.put(self.n.send(Packet(PacketType.GET, {"type": "CHANNELS"})))

        

        chat.styles.display = "block"
        channel_list.styles.display = "block"
        channel_list.root.set_label(server_info[0])
        welcome.styles.display = "none"

        channel_list.select_node(channel_list.root)
        self.ping_loop_worker = self.ping_loop()
        self.packet_handler_worker = self.packet_handler()