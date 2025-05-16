from textual.screen import ModalScreen
from textual.containers import Vertical, HorizontalGroup, Horizontal
from textual.widgets import Label, Input, TextArea, Button

from server.server import Server


DEFAULT_SERVER_DESCRIPTION = """
Hello! Welcome to your server! Here are some things you can do to make your description more interesting! :)

Styles:
[bold]This text will be bold.[/bold]

[italic]This text will be italic.[/italic]

[dim]This text will be dim.[/dim]

[underline]This text will have an underline (if you mix this with bold, it looks like a title!)[/underline]

[strike]This text will have a strike through it.[/strike]

[reverse]This text will be reversed. (the background and the foreground colours are swapped.)[/reverse]

[blink]This text will blink! (Good for getting the user's attention ;))[/blink]

[red]This text will be red, but you can replace "red" with any colour you like![/red]

[red on black]This text has a black background, and a red foreground![/red on black]


Some combined styles:
[bold underline]This text is bold, AND has an underline![/bold underline]

[bold black on yellow blink]This text is bold, will blink, its background colour is yellow, and its foreground colour is black![/bold black on yellow]
"""


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
                yield Input("My Cool Server", placeholder="Enter a server title!")

            yield Label("Server Description:")
            yield TextArea(DEFAULT_SERVER_DESCRIPTION, id="desc-input")

            with Horizontal():
                yield Button("Cancel", id="cancel-button")
                yield Button("Create", variant="primary", id="create-button")