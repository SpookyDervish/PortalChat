class Channel:
    def __init__(self, data: dict):
        self.name = data['name']
        self.id = data["channel_id"]
        self.server_id = data["server_id"]