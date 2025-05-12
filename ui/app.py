from textual.app import App, ComposeResult
from textual.widgets import Tree, Label, Rule
from textual import work
from datetime import datetime

from ui.widgets.sidebar import ServerList, ChannelList
from ui.widgets.welcome import Welcome
from ui.widgets.chat import Chat, Message
from ui.widgets.message_box import ChatArea

from server.network import Network
from server.packet import Packet, PacketType


class Portal(App):
    DEFAULT_CSS = """
    #start-rule {
        color: $background-lighten-1;
    }
    """
    

    def compose(self) -> ComposeResult:
        yield ServerList(id="sidebar")
        yield ChannelList()
        yield Chat()
        yield Welcome()
        yield ChatArea()

    def on_mount(self):
        self.n = None
        self.channel_id = None
        self.opened_server = None
        self.query_one(Chat).styles.display = "none"
        self.query_one(ChannelList).styles.display = "none"

    def on_tree_node_highlighted(self, event: Tree.NodeHighlighted):
        if self.n is None: return
        chat = self.query_one(Chat)

        data = event.node.data
        self.channel_id = data

        messages = self.n.send(Packet(PacketType.GET, {"type": "MESSAGES", "channel_id": self.channel_id})).data
        
        # delete other messages
        chat.remove_children()

        # show starting message
        chat.mount(Label(f"[b][u]Welcome![/u][/b]\n[dim]This is the start of the #{event.node.label} channel.[/dim]\n[dim]Portal has only [bold]just started development[/bold], so watch out for bugs![/dim]"))
        chat.mount(Rule(id="start-rule"))

        # add new messages
        for message in messages:
            chat.mount(Message(message[1], message[3], datetime.strptime(message[2], "%Y-%m-%d %H:%M:%S")))

    @work
    async def send_message(self, message: str):
        response = self.n.send(Packet(PacketType.MESSAGE_SEND, {"message": message, "channel_id": self.channel_id}))
        chat = self.query_one(Chat)
        
        await chat.mount(Message(response.data["message"], response.data["sender_name"], response.data["timestamp"]))

    @work(thread=True)
    def ping_loop(self):
        chat = self.query_one(Chat)

        while True:
            response = self.n.send(Packet(PacketType.PING))

            if response.packet_type == PacketType.MESSAGE_RECV and response.data["channel_id"] == self.channel_id:
                chat.mount(Message(
                    response.data["message"],
                    response.data["sender_name"],
                    response.data["timestamp"]
                ))

    def open_server(self, server_info):
        chat = self.query_one(Chat)
        channel_list = self.query_one(ChannelList)
        welcome = self.query_one(Welcome)

        self.n = Network(server_info[2]) # start a connection to the server
        channels = self.n.send(Packet(PacketType.GET, {"type": "CHANNELS"})).data

        channel_list.clear()
        for channel in channels:
            channel_id = channel[0]
            channel_name = channel[1]

            channel_list.root.add_leaf(channel_name, data=channel_id)
        channel_list.root.expand_all()

        chat.styles.display = "block"
        channel_list.styles.display = "block"
        channel_list.root.set_label(server_info[0])
        welcome.styles.display = "none"