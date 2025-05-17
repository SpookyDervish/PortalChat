from api.user import User
from api.channel import Channel


class Message:
    def __init__(self, data: dict):
        self.content = data.get("message")
        self.timestamp = data.get("timestamp")

        self.sender = User({
            "username": data.get("sender_name")
        })

        self.channel = Channel({
            "name": data.get("channel_name"),
            "id": data.get("channel_id")
        })