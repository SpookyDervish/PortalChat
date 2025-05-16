from textual.containers import Vertical, HorizontalGroup
from textual.widgets import RichLog, Button
from textual import work

from server.server import Server


class ServerView(Vertical):
    DEFAULT_CSS = """
    ServerView {
        dock: right;
        border: tall $background-lighten-2;
        max-width: 30%;

        #log {
            background: $background-darken-3;
        }

        #server-controls {
            dock: bottom;
            background: transparent;
            height: 5;
            padding: 1;
        }
    }
    """

    def __init__(self, server_title: str, server_description: str):
        self.server_title = server_title
        self.server_description = server_description
        self.server = None
        super().__init__()

    @work(thread=True, name="server-thread")
    def server_thread(self):
        self.server = Server(
            title=self.server_title,
            description=self.server_description,
            log_level=2,
            rich_log = self.console_log
        )
        self.server.log("Press <ESC> on your keyboard to close the server view. Be mindful, [b]this will also shut down the server![/b]")

    def on_button_pressed(self, event):
        if event.button.id == "stop-btn":
            self.server.stop()

    def on_mount(self):
        self.server_thread()

    def compose(self):
        self.console_log = RichLog(markup=True, id="log")
        yield self.console_log

        with HorizontalGroup(id="server-controls"):
            yield Button(label="Stop Server", variant="error", id="stop-btn")