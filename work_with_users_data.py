import sqlite3
from create_database import DB_PATH


def add_user(username, surname, name, telegram_id, subscribe=0, admin=0):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (username, surname, name, telegram_id, subscribe, admin)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (username, surname, name, telegram_id, subscribe, admin))

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        # username или telegram_id уже существует
        return False

    finally:
        conn.close()


def check_username(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT surname, name
        FROM users
        WHERE username = ?
    """, (username,))

    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0], result[1]

    return None, None


def check_surname_name(surname, name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT username
        FROM users
        WHERE surname = ? AND name = ?
    """, (surname, name))

    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]

    return None


def update_username(surname, name, new_username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE users
            SET username = ?
            WHERE surname = ? AND name = ?
        """, (new_username, surname, name))

        conn.commit()
        updated = cursor.rowcount > 0

    except sqlite3.IntegrityError:
        # новый username уже занят
        return False

    finally:
        conn.close()

    return updated


def update_surname_name(new_surname, new_name, username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET surname = ?, name = ?
        WHERE username = ?
    """, (new_surname, new_name, username))

    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()

    return updated
