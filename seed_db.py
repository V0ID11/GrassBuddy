import sqlite3
import os

DB_NAME = 'grassbuddy.db'

def seed_database():
    # Connect (this will create the file if it doesn't exist)
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    print("Cleaning up old tables...")
    try:
        c.execute("DROP TABLE IF EXISTS friends")
        c.execute("DROP TABLE IF EXISTS notifications")
        c.execute("DROP TABLE IF EXISTS photos")
        c.execute("DROP TABLE IF EXISTS users")
        print("Dropped old tables.")
    except sqlite3.OperationalError as e:
        print(f"Error dropping tables: {e}")

    print("Creating tables...")
    # Re-create tables (definitions taken from FlaskBackend.py)
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            auth_token TEXT NOT NULL UNIQUE,
            score INTEGER DEFAULT 0
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            user_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id))''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS friends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            friend_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(friend_id) REFERENCES users(id)
        )
    ''')

    print("Inserting users...")
    users = [
        ('Nick', 'auth_nick_1'),
        ('Sarah', 'auth_sarah_2'),
        ('Mike', 'auth_mike_3'),
        ('Emma', 'auth_emma_4')
    ]
    c.executemany("INSERT INTO users (name, auth_token) VALUES (?, ?)", users)
    
    # Get user Ids
    c.execute("SELECT id, name FROM users")
    db_users = {name: uid for uid, name in c.fetchall()}
    print(f"Users created: {db_users}")

    print("Establishing friendships...")
    friendships = [
        (db_users['Nick'], db_users['Sarah']),
        (db_users['Sarah'], db_users['Nick']),
        (db_users['Nick'], db_users['Mike']),
        (db_users['Mike'], db_users['Nick']),
        (db_users['Sarah'], db_users['Emma']),
        (db_users['Emma'], db_users['Sarah'])
    ]
    c.executemany("INSERT INTO friends (user_id, friend_id) VALUES (?, ?)", friendships)

    print("Adding a sample notification...")
    c.execute("INSERT INTO notifications (user_id, type, message) VALUES (?, ?, ?)", 
              (db_users['Nick'], 'NUDGE', 'Welcome to GrassBuddy! Go touch some grass.'))

    conn.commit()
    conn.close()
    print("Database seeded successfully!")

if __name__ == "__main__":
    seed_database()