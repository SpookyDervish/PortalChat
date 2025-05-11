from textual.app import App, ComposeResult

from ui.widgets.sidebar import ServerList
from ui.widgets.welcome import Welcome
from ui.widgets.chat import Chat
from ui.widgets.message_box import ChatArea


class Portal(App):
    def compose(self) -> ComposeResult:
        yield ServerList(id="sidebar")
        yield Chat()
        yield Welcome()
        yield ChatArea()

    def on_mount(self):
        self.opened_server = None
        self.query_one(Chat).styles.display = "none"

    def open_server(self, server_info):
        chat = self.query_one(Chat)
        welcome = self.query_one(Welcome)

        chat.styles.display = "block"
        welcome.styles.display = "none"