from textual.app import App, ComposeResult
from time import sleep

from ui.widgets.sidebar import ServerList, ChannelList
from ui.widgets.welcome import Welcome
from ui.widgets.chat import Chat
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
        self.opened_server = None
        self.query_one(Chat).styles.display = "none"
        self.query_one(ChannelList).styles.display = "none"

    def open_server(self, server_info):
        chat = self.query_one(Chat)
        channel_list = self.query_one(ChannelList)
        welcome = self.query_one(Welcome)

        n = Network(server_info[2]) # start a connection to the server
        channels = n.send(Packet(PacketType.GET, "CHANNELS")).data

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