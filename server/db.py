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

        self.cur.execute("INSERT INTO servers (name) VALUES (?)", ("MyServer1",))
        server1_id = self.cur.lastrowid
        self.cur.execute("INSERT INTO servers (name) VALUES (?)", ("MyServer2",))
        server2_id = self.cur.lastrowid
        
        self.cur.execute("INSERT INTO users (username) VALUES (?)", ("Alice",))
        alice_id = self.cur.lastrowid
        self.cur.execute("INSERT INTO users (username) VALUES (?)", ("Bob",))
        bob_id = self.cur.lastrowid

        print(server1_id, server2_id)
        print(alice_id, bob_id)

        # Add users to servers via memberships
        memberships = [
            (alice_id, server1_id),
            (alice_id, server2_id),
            (bob_id, server1_id),
        ]
        self.cur.executemany("INSERT INTO memberships (user_id, server_id) VALUES (?, ?)", memberships)

        self.conn.commit()

        # Query: All users in MyServer1
        self.cur.execute("""
        SELECT u.username
        FROM users u
        JOIN memberships m ON u.user_id = m.user_id
        JOIN servers s ON m.server_id = s.server_id
        WHERE s.name = ?
        """, ("MyServer1",))
        print("Users in MyServer1:", [row[0] for row in self.cur.fetchall()])

        # Query: All servers Alice is in
        self.cur.execute("""
        SELECT s.name
        FROM servers s
        JOIN memberships m ON s.server_id = m.server_id
        JOIN users u ON m.user_id = u.user_id
        WHERE u.username = ?
        """, ("Alice",))
        print("Servers Alice is in:", [row[0] for row in self.cur.fetchall()])

        self.conn.close()


if __name__ == "__main__":
    db = Database()