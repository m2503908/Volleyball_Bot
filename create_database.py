import sqlite3

DB_PATH = "users.db"


def init_db():
    """
    Функция init_db создает базу данных
    :return: ничего не возвращает, лишь создает users.db
    """
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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        form_link TEXT,
        friday INTEGER,
        saturday INTEGER
    )
    """)

    conn.commit()
    conn.close()

init_db()

