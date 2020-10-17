from random import sample
import rstr
import sqlite3

accounts = {}
running = True

conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS card (
id INTEGER PRIMARY KEY,
number TEXT NOT NULL,
pin TEXT,
balance INTEGER DEFAULT 0
);"""
            )
conn.commit()


def luhn_algorithm(card_num):
    card_list = [int(i) for i in card_num[:-1]]
    luhn = []
    last_digit = None
    for i, j in enumerate(card_list, start=1):
        if i % 2 == 1:
            j *= 2
            if j > 9:
                j -= 9
        luhn.append(j)
    for i in range(10):
        if not (sum(luhn) + i) % 10:
            last_digit = i
            break
    return card_num[:-1] + str(last_digit)


def create_ac():
    card_num = rstr.xeger('^4[0]{5}[0-9]{10}$')
    card_num = luhn_algorithm(card_num)
    print(f'\nYour card has been created\nYour card number:{card_num}')
    pin = ''.join(str(i) for i in sample([i for i in range(10)], 4))
    print(f'Your card PIN:\n{pin}')
    accounts[card_num] = pin
    cur.execute('INSERT INTO card (number, pin) VALUES (?, ?)', (card_num, pin))
    conn.commit()
    print()


def logged_in(user_card, user_pin):
    global running
    while True:
        print("""1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit"""
              )
        user_input = input()
        cur.execute('SELECT balance FROM card WHERE number=?', (user_card,))
        balance = cur.fetchone()
        balance = int(balance[0])
        if user_input == '1':
            print(f'\nBalance: {balance}\n')
        elif user_input == '2':
            income = input('\nEnter income:\n')
            cur.execute('UPDATE card SET balance = balance + ? WHERE (number=? AND pin=?)',
                        (income, user_card, user_pin))
            conn.commit()
            print('Income was added!')
        elif user_input == '3':
            checks = 0
            print('Transfer')
            transfer_number = input()
            if transfer_number == user_card:
                print("You can't transfer money to the same account!")
            else:
                checks += 1
            if luhn_algorithm(transfer_number) != transfer_number:
                print('Probably you made mistake in the card number. Please try again!')
            else:
                checks += 1
            cur.execute('SELECT * FROM card WHERE number=?', (transfer_number,))
            if cur.fetchone() is None:
                print('Such a card does not exist.')
            else:
                checks += 1
            if checks == 3:
                transfer_money = int(input('Enter how much money you want to transfer:\n'))
                if transfer_money > balance:
                    print('Not enough money!')
                else:
                    print('Success!')
                    cur.execute('UPDATE card SET balance = balance + ? WHERE number=?',
                                (transfer_money, transfer_number))
                    cur.execute('UPDATE card SET balance = balance - ? WHERE number=?', (transfer_money, user_card))
                    conn.commit()
        elif user_input == '4':
            cur.execute('DELETE FROM card WHERE number = ?', (user_card,))
            conn.commit()
            break
        elif user_input == '5':
            print('\nYou have successfully logged out!')
            break
        elif user_input == '0':
            running = False
            break
    print()


def log_in():
    user_card = input('\nEnter your card number:\n')
    user_pin = input('Enter your PIN:\n')
    print()
    cur.execute('SELECT * from card WHERE (number=? AND pin=?)', (user_card, user_pin))
    if cur.fetchone() is not None:
        print('You have successfully logged in!\n')
        logged_in(user_card, user_pin)
    else:
        print('Wrong card number or PIN!\n')


while running:
    print("""1. Create an account
2. Log into account
0. Exit""")
    menu_input = input()
    if menu_input == '1':
        create_ac()
    elif menu_input == '2':
        log_in()
    elif menu_input == '0':
        running = False

conn.close()
