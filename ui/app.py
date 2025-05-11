from textual.app import App, ComposeResult

from ui.widgets.sidebar import ServerList
from ui.widgets.welcome import Welcome
from ui.widgets.chat import Chat
from ui.widgets.message_box import ChatArea

from server.packet import Packet, PacketType
from server.network import Network

from time import sleep


class Portal(App):
    def compose(self) -> ComposeResult:
        yield ServerList()
        yield Chat()
        yield Welcome()
        yield ChatArea()

    def on_mount(self):
        self.query_one(Chat).styles.display = "none"