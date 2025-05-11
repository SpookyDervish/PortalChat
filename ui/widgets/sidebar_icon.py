from textual.widgets import Button
from util import abbreviate


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