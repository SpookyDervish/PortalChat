class User:
    def __init__(self, data: dict):
        self.user_name = data["username"]
        self.uuid = data["uuid"]

    def __str__(self):
        return f"@{self.user_name}"

    def __repr__(self):
        return f"({self.user_name} : {self.uuid})"