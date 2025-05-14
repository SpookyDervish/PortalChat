from textual.containers import VerticalScroll, Vertical
from textual.widgets import Tree
from textual.widgets import Button, Rule

from ui.widgets.add_server import AddServer
from ui.widgets.settings_menu import SettingsScreen


class ChannelList(Tree):
    DEFAULT_CSS = """
    ChannelList {
        dock: left;
        max-width: 25;
        margin-left: 10;
    }
    """

    def __init__(self):
        super().__init__("Channels", id="channels")

class ServerList(Vertical):
    DEFAULT_CSS = """
    ServerList {
        width: 10;
        background: $background-lighten-1;
        padding: 1;
        height: 100%;
        dock: left;
        margin-right: 1;

        .side-btn {
            max-width: 8;
            height: 3;
            margin-bottom: 1;
        }

        Rule {
            color: $background-lighten-3;
        }
    }
    """

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "add-server-btn":
            self.app.push_screen(AddServer())
        elif event.button.id == "settings-btn":
            self.app.push_screen(SettingsScreen())

        if "server-btn" in event.button.classes:
            self.app.open_server(event.button.info)

    def compose(self):
        yield VerticalScroll(id="icons")
        yield Rule()
        yield Button("+", variant="primary", id="add-server-btn", classes="side-btn")
        yield Button("⚙", id="settings-btn", classes="side-btn")