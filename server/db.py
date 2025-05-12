import sqlite3


class Database:
    def __init__(self):
        self.conn = sqlite3.connect("portal_db.db")
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
            user_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL
        );
        ''')

        # create a table of memberships for each server
        self.cur.execute('''
        CREATE TABLE IF NOT EXISTS memberships (
            user_id INTEGER,
            server_id INTEGER,
            PRIMARY KEY (user_id, server_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (server_id) REFERENCES servers(server_id) ON DELETE CASCADE
        );
        ''')
        self.commit()

        server_id = self.create_server("Testing Server")
        server2_id = self.create_server("Testing Server 2")
        user_id = self.create_user("SpookyDervish")

        self.add_user_to_server(user_id, server_id)

        print(self.users_in_server("Testing Server"))
        print(self.is_user_in_server(user_id, server_id))
        print(self.is_user_in_server(user_id, server2_id))

        self.close()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

    def create_server(self, server_name: str):
        self.cur.execute("INSERT INTO servers (name) VALUES (?)", (server_name,))
        server_id = self.cur.lastrowid
        return server_id
    
    def create_user(self, user_name: str):
        self.cur.execute("INSERT INTO users (username) VALUES (?)", (user_name,))
        user_id = self.cur.lastrowid
        return user_id
    
    def add_user_to_server(self, user_id: int, server_id: int):
        if self.is_user_in_server(user_id, server_id):
            return

        memberships = [
            (user_id, server_id)
        ]
        self.cur.executemany("INSERT INTO memberships (user_id, server_id) VALUES (?, ?)", memberships)

    def user_exists(self, user_id: int):
        self.cur.execute("SELECT 1 FROM users WHERE user_id = ? LIMIT 1", (user_id,))
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

    def is_user_in_server(self, user_id: int, server_id: int):
        self.cur.execute("""
            SELECT 1 FROM memberships
            WHERE user_id = ? AND server_id = ?
            LIMIT 1
        """, (user_id, server_id))
        return self.cur.fetchone() is not None

    def users_in_server(self, server_name: str):
        self.cur.execute("""
        SELECT u.username
        FROM users u
        JOIN memberships m ON u.user_id = m.user_id
        JOIN servers s ON m.server_id = s.server_id
        WHERE s.name = ?
        """, (server_name,))
        return [row[0] for row in self.cur.fetchall()]
    
    def servers_with_user(self, user_name: str):
        self.cur.execute("""
        SELECT s.name
        FROM servers s
        JOIN memberships m ON s.server_id = m.server_id
        JOIN users u ON m.user_id = u.user_id
        WHERE u.username = ?
        """, (user_name,))
        return [row[0] for row in self.cur.fetchall()]


if __name__ == "__main__":
    db = Database()