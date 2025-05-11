from textual.containers import VerticalScroll, Vertical
from textual.widgets import Button, Rule
from util import abbreviate

from ui.widgets.add_server import AddServer


class Icon(Button):
    DEFAULT_CSS = """
    Icon {
        border: tall black;
        text-align: center;
    }
    """

    def __init__(self, name: str):
        self.server_name = name
        super().__init__(abbreviate(self.server_name), tooltip=self.server_name, classes="side-btn")

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
            self.app.notify("Sorry! The settings menu isn't implemented yet!", title="Woops!", severity="warning")

    def compose(self):
        with VerticalScroll():
            yield Icon("Testing Server")
        yield Rule()
        yield Button("+", variant="primary", id="add-server-btn", classes="side-btn")
        yield Button("⚙", id="settings-btn", classes="side-btn")