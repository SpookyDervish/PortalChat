from textual.app import App, ComposeResult

from ui.widgets.sidebar import ServerList, ChannelList
from ui.widgets.welcome import Welcome
from ui.widgets.chat import Chat
from ui.widgets.message_box import ChatArea

from api.channel import Channel


channel = Channel("test-channel")


class Portal(App):
    def compose(self) -> ComposeResult:
        yield ServerList(id="sidebar")
        yield ChannelList()
        yield Chat(channel)
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

        chat.styles.display = "block"
        channel_list.styles.display = "block"
        channel_list.root.set_label(server_info[0])
        welcome.styles.display = "none"