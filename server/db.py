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
        user_id = self.create_user("SpookyDervish")

        self.add_user_to_server(user_id, server_id)

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
        memberships = [
            (user_id, server_id)
        ]
        self.cur.executemany("INSERT INTO memberships (user_id, server_id) VALUES (?, ?)", memberships)

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