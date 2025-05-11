from textual.containers import Container
from textual.widgets import Input
from textual.app import ComposeResult


class ChatArea(Container):
    DEFAULT_CSS = """
    ChatArea {
        height: 3;
        margin: 0 1 1 1;
    }
    """
    
    def compose(self) -> ComposeResult:
        yield Input(placeholder="Type your really cool message here!", id="msg-input")