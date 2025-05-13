from textual.containers import Vertical
from textual.widgets import Label

from textual.markup import MarkupError


class ServerOverview(Vertical):
    DEFAULT_CSS = """
    ServerOverview {
        align: center middle;

        Label {
            width: auto;
            text-align: center;
            min-width: 50%;
        }
    }
    """
    

    def __init__(self, server_info: dict):
        super().__init__()
        self.info = server_info

    def compose(self):
        final_text = f"[b u]Welcome to {self.info['title']}[/b u]\n[b]Online: [green]{self.info['online']}[/green][/b]\n\n{self.info['description']}"
        label = Label(final_text)

        try:
            label.visual
        except MarkupError:
            label = Label(final_text, markup=False)

        yield label