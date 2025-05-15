import sqlite3


class Database:
    def __init__(self, server):
        self.server = server

        # ! Disabling check_same_thread fixes a lot of issues, but corruption could be a REALLY big problem, might need to check this.
        self.conn = sqlite3.connect("portal_db.db", check_same_thread=False)
        self.cur = self.conn.cursor()

        # Create a table for servers
        # each server has an ID whcih won't have a duplicate, and it is the key
        # each server has a string name, which can't be null
        self.cur.execute('''
        CREATE TABLE IF NOT EXISTS servers (
            server_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        );
        ''')

        # create a table of users
        # each user has a non-duplicate ID which is used as the key
        # each user has a username which can't be null
        self.cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_uuid TEXT PRIMARY KEY,
            username TEXT NOT NULL
        );
        ''')

        # create a table of memberships for each server
        # each membership links a user id to a server id
        self.cur.execute('''
        CREATE TABLE IF NOT EXISTS memberships (
            user_uuid TEXT,
            server_id INTEGER,
            PRIMARY KEY (user_uuid, server_id),
            FOREIGN KEY (user_uuid) REFERENCES users(user_uuid) ON DELETE CASCADE,
            FOREIGN KEY (server_id) REFERENCES servers(server_id) ON DELETE CASCADE
        );
        ''')

        # create a table of channels
        # each channel has an id which cannot be a duplicate, and it is the key
        # each channel has a name which can't be null
        # each channel has a server id
        # each channel id references a server id
        self.cur.execute('''
        CREATE TABLE IF NOT EXISTS channels (
            channel_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            server_id INTEGER,
            FOREIGN KEY (server_id) REFERENCES servers(server_id) ON DELETE CASCADE
        );
        ''')

        # create a table of messages
        # each message has an id which can't be a duplicate and is the key
        # each message has content
        # each message has a timestamp
        # each message has a user id
        # each message has a channel id
        # each message links the user id
        # each message links the channel id
        self.cur.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            message_id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_uuid TEXT,
            user_name TEXT,
            channel_id INTEGER,
            FOREIGN KEY (user_uuid) REFERENCES users(user_uuid) ON DELETE SET NULL,
            FOREIGN KEY (channel_id) REFERENCES channels(channel_id) ON DELETE CASCADE
        );
        ''')
        self.commit()

        server_id = self.get_server_by_name(self.server.server_info["title"])
        if not server_id:
            server_id = self.create_server(self.server.server_info["title"])
        else:
            server_id = server_id[0]

        channel_id = self.get_channel_by_name(server_id, "general")
        if not channel_id:
            channel_id = self.create_channel_in_server(server_id, "general")

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

    def update_username(self, member_id: id, new_username: str):
        self.cur.execute("""
            UPDATE members SET name = ?
            WHERE member_id = ?
        """, (new_username, member_id))

    def get_channel_name_by_id(self, channel_id: int):
        self.cur.execute("""
            SELECT name FROM channels
            WHERE channel_id = ?
            LIMIT 1
        """, (channel_id,))
        result = self.cur.fetchone()
        return result[0] if result else None

    def get_server_from_channel(self, channel_id: int):
        self.cur.execute("""
            SELECT s.*
            FROM servers s
            JOIN channels c ON s.server_id = c.server_id
            WHERE c.channel_id = ?
            LIMIT 1
        """, (channel_id,))
        server = self.cur.fetchone()
        return server

    def get_user_by_name(self, username: str):
        self.cur.execute("""
            SELECT * FROM users
            WHERE username = ?
            LIMIT 1
        """, (username,))
        return self.cur.fetchone()

    def get_server_by_name(self, server_name: str):
        self.cur.execute("""
            SELECT server_id, name FROM servers
            WHERE name = ?
            LIMIT 1
        """, (server_name,))
        return self.cur.fetchone()

    def get_channels_in_server(self, server_id: int):
        self.cur.execute("""
            SELECT channel_id, name FROM channels
            WHERE server_id = ?
        """, (server_id,))
        return self.cur.fetchall()
    
    def get_channels_by_server_name(self, server_name: str):
        self.cur.execute("""
            SELECT c.channel_id, c.name
            FROM channels c
            JOIN servers s ON c.server_id = s.server_id
            WHERE s.name = ?
        """, (server_name,))
        return self.cur.fetchall()
    
    def get_messages_in_channel(self, channel_id: int):
        self.cur.execute("""
            SELECT m.message_id, m.content, m.timestamp, u.username
            FROM messages m
            LEFT JOIN users u ON m.user_uuid = u.user_uuid
            WHERE m.channel_id = ?
            ORDER BY m.timestamp ASC
        """, (channel_id,))
        return self.cur.fetchall()
    
    def get_channel_by_name(self, server_id: int, channel_name: str):
        self.cur.execute("""
            SELECT * FROM channels
            WHERE server_id = ? AND name = ?
            LIMIT 1
        """, (server_id, channel_name))
        return self.cur.fetchone()
    
    def create_channel_in_server(self, server_id: int, channel_name: str):
        if self.get_channel_by_name(server_id, channel_name):
            return

        # Check if the server exists
        self.cur.execute("SELECT 1 FROM servers WHERE server_id = ? LIMIT 1", (server_id,))
        if self.cur.fetchone() is None:
            raise ValueError(f"Server ID {server_id} does not exist.")

        # Insert the new channel
        self.cur.execute("""
            INSERT INTO channels (name, server_id)
            VALUES (?, ?)
        """, (channel_name, server_id))

        return self.cur.lastrowid  # Return the new channel's ID
    
    def create_message_in_channel(self, channel_id: int, user_uuid: str, user_name: str, content: str):
        # Check if the channel exists
        self.cur.execute("SELECT 1 FROM channels WHERE channel_id = ? LIMIT 1", (channel_id,))
        if self.cur.fetchone() is None:
            raise ValueError(f"Channel ID {channel_id} does not exist.")

        # Optional: check if user exists (or let NULL be inserted)
        self.cur.execute("SELECT 1 FROM users WHERE user_uuid = ? LIMIT 1", (user_uuid,))
        if self.cur.fetchone() is None:
            raise ValueError(f"User UUID {user_uuid} does not exist.")

        # Insert the message
        self.cur.execute("""
            INSERT INTO messages (content, user_uuid, user_name, channel_id)
            VALUES (?, ?, ?, ?)
        """, (content, user_uuid, user_name, channel_id))

        return self.cur.lastrowid  # Return the new message's ID

    def create_server(self, server_name: str):
        if self.get_server_by_name(server_name):
            raise ValueError("Server with that name already exists!")

        self.cur.execute("INSERT INTO servers (name) VALUES (?)", (server_name,))
        server_id = self.cur.lastrowid
        return server_id
    
    def create_user(self, user_name: str, uuid: str):
        if self.get_user_by_name(user_name):
            raise ValueError(f"A user with the name \"{user_name}\" already exists!")

        self.cur.execute("INSERT INTO users (user_uuid, username) VALUES (?, ?)", (uuid,user_name))
        user_uuid = self.cur.lastrowid
        return user_uuid
    
    def add_user_to_server(self, user_uuid: str, server_id: int):
        if self.is_user_in_server(user_uuid, server_id):
            return

        memberships = [
            (user_uuid, server_id)
        ]
        self.cur.executemany("INSERT INTO memberships (user_uuid, server_id) VALUES (?, ?)", memberships)

    def user_exists(self, user_uuid: str):
        self.cur.execute("SELECT 1 FROM users WHERE user_uuid = ? LIMIT 1", (user_uuid,))
        return self.cur.fetchone() is not None

    def user_exists_by_name(self, username: str):
        self.cur.execute("SELECT 1 FROM users WHERE username = ? LIMIT 1", (username,))
        return self.cur.fetchone() is not None
    
    def server_exists(self, server_id: int):
        self.cur.execute("SELECT 1 FROM servers WHERE server_id = ? LIMIT 1", (server_id,))
        return self.cur.fetchone() is not None
    
    def server_exists_by_name(self, name: str):
        self.cur.execute("SELECT 1 FROM servers WHERE name = ? LIMIT 1", (name,))
        return self.cur.fetchone() is not None

    def is_user_in_server(self, user_uuid: str, server_id: int):
        self.cur.execute("""
            SELECT 1 FROM memberships
            WHERE user_uuid = ? AND server_id = ?
            LIMIT 1
        """, (user_uuid, server_id))
        return self.cur.fetchone() is not None

    def users_in_server(self, server_name: str):
        self.cur.execute("""
        SELECT u.username
        FROM users u
        JOIN memberships m ON u.user_uuid = m.user_uuid
        JOIN servers s ON m.server_id = s.server_id
        WHERE s.name = ?
        """, (server_name,))
        return [row[0] for row in self.cur.fetchall()]
    
    def servers_with_user(self, user_name: str):
        self.cur.execute("""
        SELECT s.name
        FROM servers s
        JOIN memberships m ON s.server_id = m.server_id
        JOIN users u ON m.user_uuid = u.user_uuid
        WHERE u.username = ?
        """, (user_name,))
        return [row[0] for row in self.cur.fetchall()]