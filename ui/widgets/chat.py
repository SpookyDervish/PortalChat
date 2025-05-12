from textual.containers import VerticalScroll, Vertical
from textual.widgets import Label, Rule
from datetime import datetime

from api.channel import Channel
from ui.widgets.image import Image


class Message(Vertical):
    DEFAULT_CSS = """
    Message {
        min-height: 2;
        max-height: 3;
        height: 2;
        margin-bottom: 1;
    }

    Message .user-icon {
        dock: left;   
        width: 4;
        margin-right: 1;
    }
    """
    

    def __init__(self, content: str, user_name: str, send_time: datetime, sender_icon_path: str = "assets/images/default_user.png"):
        super().__init__()
        self.content = content
        self.user_name = user_name
        self.send_time = send_time
        self.sender_icon_path = sender_icon_path

    def compose(self):
        yield Image(self.sender_icon_path, (4, 4), classes="user-icon")
        yield Label(f"[bold]@{self.user_name}[/bold] [dim]({self.send_time.strftime('%I:%M %p')})[/dim]", classes="user-name")
        yield Label(self.content, classes="msg-content")

class Chat(VerticalScroll):
    DEFAULT_CSS = """
    Chat {
        padding: 1;
    }
    """
    
    def __init__(self):
        super().__init__()