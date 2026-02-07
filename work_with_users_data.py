import csv

def add_user(username, surname, name, telegram_id, subscribe=1, admin=0):
    with open('users_data.csv', newline='', mode='a') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow([username, surname, name, telegram_id, subscribe, admin])


def check_user(username):
    with open('users_data.csv') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if row['username'] == username:
                return row['surname'], row['name']
    return None, None