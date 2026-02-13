import sqlite3
from create_database import DB_PATH


def add_user(username: str, surname: str, name: str, telegram_id: int, subscribe=int(0), admin=int(0)) -> bool:
    """
    Функция add_user добавляет пользователя в бд, в таблицу users
    :param username: ник в телеграм пользователя
    :param surname: фамилия пользователя
    :param name: имя пользователя
    :param telegram_id: телеграм id пользователя
    :param subscribe: является ли пользователь абониментом
    :param admin: является ли пользователь админом
    :return: меняет бд и выводит True, если все прошло успешно и False, если с ошибкой
    """
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


def add_link_db(date: str, link: str, friday: int, saturday: int):
    """
    Функция add_link_db добавляет ссылку на гугл форму и информацию о ней
    :param date: дата отправки ссылки (впоследствии оказалось, что это возможно лишняя информация)
    :param link: строка со ссылкой
    :param friday: информация о том, сколько людей придет в пятницу на игру. Добавляется не одновременно с самой ссылкой
    :param saturday: информация о том, сколько людей придет в субботу на игру. Добавляется не одновременно с самой ссылкой
    :return: нет вывода, функция изменяют саму бд непосредственно
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO links (date, form_link, friday, saturday) 
        VALUES (?, ?, ?, ?)
    """, (date, link, friday, saturday))

    conn.commit()
    conn.close()


def get_last_link() -> str:
    """
    Функция get_last_link выводит информацию о ссылке из последней строки таблицы links
    :return: строка с информацией о ссылке
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT form_link
        FROM links
        ORDER BY id
        DESC LIMIT 1
    """)

    result = cursor.fetchone()
    conn.close()

    return result[0]


def find_admin() -> list:
    """
    Функция просматривает таблицу users и ищет пользователей с admin = 1
    :return: список с telegram_id пользователей, у которых есть права админа
    """
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



def find_subscribe() -> list:
    """
    Функция find_subscribe ищет абониментов среди всех пользователей
    :return: список telegram_id пользователей у которых в бд subscribe = 1
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT telegram_id
        FROM users
        WHERE subscribe = 1
    """)

    result = cursor.fetchall()
    conn.close()

    return [row[0] for row in result]


def get_surname_name() -> list:
    """
    Функция get_surname_name получается фамилия и имена всех пользователей из бд
    :return: список с элементами в формате 'Фамилия Имя'
    """
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


def check_username(username: str) -> tuple:
    """
    Функция check_username проверяет существует ли в бд пользователь с таким username
    :param username: строка с проверяемым юзернеймом
    :return: кортеж с фамилией или кортеж с None
    """
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


def check_surname_name(surname: str, name: str) -> str or None:
    """
    Функция check_surname_name проверяет существует ли в бд пользователь с указанными имем и фамилией
    :param surname: строка с фамилией
    :param name: строка с именем
    :return: строка с юзернеймом искомого пользователя или None
    """
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


def get_id_by_name(surname: str, name: str) -> str:
    """
    Функция get_id_by_name вовзращает telegram_id пользователя по его Фамилии и имени
    :param surname: Фамилия пользователя (строка)
    :param name: Имя пользователя (строка)
    :return: строка с telegram_id пользователя
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT telegram_id
        FROM users
        WHERE surname = ? AND name = ?
    """, (surname, name))

    result = cursor.fetchone()
    conn.close()

    return result[0]


def update_username(surname: str, name: str, new_username: str) -> bool:
    """
    Функция update_username ищет пользователя по фамилии и имени и заносит в бд новый юзернейм
    :param surname: строка с фамилией
    :param name: строка с именем
    :param new_username: строка с новым юзернеймом
    :return: обновляет бд, возвращает True если все успешно; False если не успешно
    """
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


def update_surname_name(new_surname: str, new_name: str, username: str) -> bool:
    """
    Функция update_surname_name обновляет фамилию и имя пользователя по юзернейму
    :param new_surname: строка с новой фамилией
    :param new_name: строка с новым именем
    :param username: строка с искомым юзернеймом
    :return: меняет бд напрямую; возращает True, False в зависимости от успеха выполнения программы
    """
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


def change_rights(surname: str, name: str, role: str, flag: str) -> bool:
    """
    Функция change_rights изменяет значение subsscribe или admin на значение переменной flag (0 или 1) для указанного пользователя
    :param surname: Фамилия пользователя
    :param name: Имя пользователя
    :param role: Строка в которой содержится admin или subscribe для указания нужного столбца
    :param flag: Значение, на которое надо поменять текущее (0 или 1)
    :return: Производит изменения в бд, на вывод подает True или False, чтобы определить, успешно завершилась функция или нет
    """
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


def update_friday_saturday(friday: str, saturday: str) -> bool:
    """
    Функция update_friday_saturday меняет значения в соответствующих колонках таблицы links
    :param friday: как изменить значение в колонке friday, обычно 0 или 1
    :param saturday: как изменить значение в колонке saturday, обычно 0 или 1
    :return: меняет саму бд; True/False для проверки
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE links
        SET friday = friday + ?,
            saturday = saturday + ?
        WHERE id = (SELECT MAX(id) FROM links)
    """, (friday, saturday))

    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()

    return updated