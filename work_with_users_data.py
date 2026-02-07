import csv

def add_user(username, surname, name, telegram_id, subscribe=1, admin=0):
    with open('users_data.csv', newline='', mode='a') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow([username, surname, name, telegram_id, subscribe, admin])


def check_username(username):
    with open('users_data.csv') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if row['username'] == username:
                return row['surname'], row['name']
    return None, None


def check_surname_name(surname, name):
    with open('users_data.csv') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if row['surname'] == surname and row['name'] == name:
                return row['username']
    return None


def update_username(surname, name, new_username):
    with open('users_data.csv') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if row['surname'] == surname and row['name'] == name:
                row['username'] = new_username


def update_surname_name(new_surname, new_name, username):
    with open('users_data.csv') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if row['username'] == username:
                row['surname'] = new_surname
                row['name'] = new_name