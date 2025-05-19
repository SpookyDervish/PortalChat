from api.user import User
from api.channel import Channel


class Message:
    def __init__(self, data: dict, server):
        self.content: str = data.get("message")
        self.timestamp = data.get("timestamp")

        self.sender = User({
            "username": data.get("sender_name"),
            "uuid": data.get("sender_uuid")
        })

        self.channel = Channel({
            "name": data.get("channel_name"),
            "channel_id": data.get("channel_id"),
            "server_id": data.get("server_id")
        }, server)

        self.server = server

    def __repr__(self):
        return f"@{self.sender.user_name}: {self.content}"