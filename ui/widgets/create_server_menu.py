from textual.screen import ModalScreen
from textual.containers import Vertical, HorizontalGroup, Horizontal
from textual.widgets import Label, Input, TextArea, Button

from server.server import Server


class CreateServerScreen(ModalScreen):
    DEFAULT_CSS = """
    CreateServerScreen {
        align: center middle;

        #window {
            max-width: 50%;
            max-height: 75%;
            border: panel $primary;
            border-title-align: center;
            padding: 3 3 0 3;

            HorizontalGroup {
                margin-bottom: 1;

                Label {
                    height: 3;
                    content-align: left middle;
                }
            }

            Horizontal {
                layout: grid;
                grid-size: 2 1;
                height: 3;
                dock: bottom;
                align: center middle;
                margin-top: 1;
            }

            #desc-input {
                margin-top: 1;
            }
        }
    }
    """

    def on_key(self, event):
        if event.key == "escape":
            self.dismiss()

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "cancel-button":
            self.dismiss()
        elif event.button.id == "create-button":
            self.notify("W.I.P", severity="warning")

    def compose(self):
        with Vertical(id="window") as window:
            window.border_title = "=== Start Server ==="
            with HorizontalGroup():
                yield Label("Server title:")
                yield Input(placeholder="Enter a server title!")

            yield Label("Server Description:")
            yield TextArea("the [bold yellow reverse]COOLEST[/bold yellow reverse] server", language="xml", id="desc-input")

            with Horizontal():
                yield Button("Cancel", id="cancel-button")
                yield Button("Create", variant="primary", id="create-button")