from textual.screen import ModalScreen
from textual.containers import Vertical, HorizontalGroup, Middle
from textual.widgets import Label, Input, TextArea


class CreateServerScreen(ModalScreen):
    DEFAULT_CSS = """
    CreateServerScreen {
        align: center middle;

        #window {
            max-width: 50%;
            max-height: 75%;
            border: panel $primary;
            border-title-align: center;
            padding: 3;

            HorizontalGroup {
                margin-bottom: 1;

                Label {
                    height: 3;
                    content-align: left middle;
                }
            }
        }
    }
    """

    def on_key(self, event):
        if event.key == "escape":
            self.dismiss()

    def compose(self):
        with Vertical(id="window") as window:
            window.border_title = "=== Start Server ==="
            with HorizontalGroup():
                yield Label("Server title:")
                yield Input()

            yield Label("Server Description:")
            yield TextArea(language="markup")