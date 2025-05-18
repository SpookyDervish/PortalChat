from textual.containers import VerticalGroup, HorizontalGroup
from textual.widgets import RichLog, Button
from textual import work

from server.server import Server
from threading import Thread


class ServerView(VerticalGroup):
    DEFAULT_CSS = """
    ServerView {
        dock: right;
        border: tall $background-lighten-2;
        width: 30%;
        min-width: 50;

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

        self.console_log = RichLog(markup=True, id="log", wrap=True)

        self.server = Server(
            title=self.server_title,
            description=self.server_description,
            log_level=1,
            rich_log = self.console_log,
            interactive=False
        )
        super().__init__()

    def on_key(self, event):
        if event.key == "escape":
            if self.server.running:
                self.notify("Stopping server...")
                self.server.stop()
            self.remove()

    def on_button_pressed(self, event):
        if event.button.id == "stop-btn":
            if self.server.running:
                self.notify("Stopping server...")
                self.server.stop()
            else:
                self.notify("Server is already stopped! Press <ESC> on your keyboard to close the server view.")

    def on_mount(self):
        self.server_thread = Thread(target=self.server.start)
        self.server_thread.start()

        self.server.log("[bold blue]Portal Server View:[/bold blue] Press <ESC> on your keyboard to close the server view, but be careful, [b]this will also shut down the server![/b]")

    def compose(self):
        yield self.console_log

        with HorizontalGroup(id="server-controls"):
            yield Button(label="Stop Server", variant="error", id="stop-btn")