from textual.app import App, ComposeResult
from textual.widgets import Tree
from datetime import datetime

from ui.widgets.sidebar import ServerList, ChannelList
from ui.widgets.welcome import Welcome
from ui.widgets.chat import Chat, Message
from ui.widgets.message_box import ChatArea

from server.network import Network
from server.packet import Packet, PacketType


class Portal(App):
    def compose(self) -> ComposeResult:
        yield ServerList(id="sidebar")
        yield ChannelList()
        yield Chat()
        yield Welcome()
        yield ChatArea()

    def on_mount(self):
        self.n = None
        self.opened_server = None
        self.query_one(Chat).styles.display = "none"
        self.query_one(ChannelList).styles.display = "none"

    def on_tree_node_highlighted(self, event: Tree.NodeHighlighted):
        if self.n is None: return
        chat = self.query_one(Chat)

        data = event.node.data

        messages = self.n.send(Packet(PacketType.GET, {"type": "MESSAGES", "channel_id": data})).data
        
        chat.remove_children()
        for message in messages:
            chat.mount(Message(message[1], message[3], datetime.strptime(message[2], "%Y-%m-%d %H:%M:%S")))

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