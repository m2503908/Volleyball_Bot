import sqlite3

DB_PATH = "users.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        surname TEXT,
        name TEXT,
        telegram_id INTEGER UNIQUE,
        subscribe INTEGER DEFAULT 0,
        admin INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()
