class Channel:
    def __init__(self, data: dict, server):
        self.name = data.get("name")
        self.id = data.get("channel_id")
        self.server_id = data.get("server_id")

        self.server = server

    def send(self, message: str):
        """Send a system message to the channel."""
        # send a system message to the channel and let the server deal with it lmao
        self.server.send_message(message, self.id, None, None) 