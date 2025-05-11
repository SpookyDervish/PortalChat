from textual.widgets import Button
from util import abbreviate


class Icon(Button):
    DEFAULT_CSS = """
    Icon {
        border: tall black;
        text-align: center;
    }
    """

    def __init__(self, info: dict, is_server):
        self.info = info
        self.server_name = info[0]
        super().__init__(abbreviate(self.server_name), tooltip=self.server_name, classes=f"side-btn{' server-btn' if is_server else ''}")