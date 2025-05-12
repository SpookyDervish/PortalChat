from api.user import User
from datetime import datetime


class ChannelMessage:
    def __init__(self, sender: User, content: str, send_time: datetime):
        self.sender = sender
        self.content = content
        self.send_time = send_time

class Group:
    def __init__(self, name: str):
        self.name = name
        self.channels = []

class Channel:
    def __init__(self, name: str, group: Group = None, description: str = ""):
        self.name = name
        self.description = description
        self.group = group

        self.messages: list[ChannelMessage] = []

        if self.group:
            self.group.channels.append(self)

    def add_message(self, message: ChannelMessage):
        self.messages.append(message)