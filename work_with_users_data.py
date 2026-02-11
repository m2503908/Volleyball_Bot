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


def find_admin():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT telegram_id
        FROM users
        WHERE admin = 1
    """)

    result = cursor.fetchall()
    conn.close()

    return [row[0] for row in result]


def get_surname_name():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT surname, name
        FROM users
        WHERE surname IS NOT NULL
          AND name IS NOT NULL
    """)

    result = cursor.fetchall()
    conn.close()

    return [row[0] + ' ' + row[1] for row in result]


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


def change_rights(surname: str, name: str, role, flag):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(f"""
        UPDATE users
        SET {role} = ?
        WHERE surname = ? AND name = ?
    """, (flag, surname, name))

    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()

    return updated