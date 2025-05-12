from textual.containers import Container
from textual.widgets import Input
from textual.app import ComposeResult
from textual import on


class ChatArea(Container):
    DEFAULT_CSS = """
    ChatArea {
        height: 3;
        margin: 0 1 1 1;
    }
    """

    @on(Input.Submitted)
    def send_message(self, event: Input.Submitted):
        text = event.value.strip()

        if text == "":
            return

        self.query_one(Input).clear()
        self.app.send_message(text)
    
    def compose(self) -> ComposeResult:
        yield Input(placeholder="Type your really cool message here!", id="msg-input")