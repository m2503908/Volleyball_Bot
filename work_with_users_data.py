import csv

def add_user(username, surname, name, telegram_id, subscribe=1, admin=0):
    with open('users_data.csv', newline='', mode='a') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow([username, surname, name, telegram_id, subscribe, admin])
