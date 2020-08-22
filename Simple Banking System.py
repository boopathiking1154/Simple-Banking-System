import random
import sys
import sqlite3
from sqlite3 import Error


def connect_database(db_name):
    """Establish connection to database and return connection object"""
    try:
        conn = sqlite3.connect(db_name)
        return conn
    except Error as e:
        print(e)
        sys.exit()


class Banking:

    def __init__(self):
        """Initializing the Banking class and creating the table"""
        self.card = None
        self.db = connect_database('card.s3db')
        create_card = """CREATE TABLE IF NOT EXISTS card (
                                id INTEGER PRIMARY KEY,
                                number TEXT,
                                pin TEXT,
                                balance INTEGER DEFAULT 0
                                );"""
        self.c = self.db.cursor()
        self.c.execute(create_card)
        self.initial_option()

    def initial_option(self):
        """Initial options shown for creating new account or login to existing account"""
        print("1. Create an account \n2. Log into account \n0. Exit")
        option = int(input())
        print()
        if option == 1:
            self.create_account()
        if option == 2:
            self.login_account()
        if option == 0:
            print("Bye!")
            self.close_db()

    def create_account(self):
        """Function to create new account and print details"""
        while True:
            account_id = '400000'
            temp_bank_id = str(random.randint(000000000, 999999999))
            bank_id_number = (9 - len(temp_bank_id)) * '0' + temp_bank_id
            check_sum = str(self.luhn_algorithm(account_id + bank_id_number, 0))
            new_card_no = account_id + bank_id_number + check_sum
            if new_card_no not in self.get_exist_cards():
                new_card = new_card_no
                new_pin = str(random.randint(0000, 9999))
                new_pin = '0' * (4 - len(new_pin)) + new_pin
                self.c.execute('''INSERT INTO card (number, pin) VALUES(?, ?)''', (new_card, new_pin))
                self.db.commit()
                print("Your card has been created")
                print("Your card number:")
                print(new_card)
                print("Your card PIN:")
                print(new_pin)
                break
        print()
        self.initial_option()

    def login_account(self):
        """Function for login into account"""
        print("Enter your card number:")
        card_no = input()
        print("Enter your PIN:")
        pin = input()
        print()
        if card_no in self.get_exist_cards() and pin == self.get_pin(card_no):
            if self.luhn_algorithm(card_no, 1):
                print("You have successfully logged in!")
                print()
                self.card = card_no
                self.account_option()
        print("Wrong card number or PIN!")
        print()
        self.initial_option()

    def account_option(self):
        """To list options after login and call the required function"""
        print("1. Balance \n2. Add income \n3. Do transfer \n4. Close account \n5. Log out \n0. Exit")
        acc_option = int(input())
        print()
        if acc_option == 1:
            print("Balance:", self.get_balance(self.card))
            print()
            self.account_option()
        if acc_option == 2:
            self.add_income()
            print()
            self.account_option()
        if acc_option == 3:
            self.transfer_amount()
            print()
            self.account_option()
        if acc_option == 4:
            self.close_acc()
            print()
            self.initial_option()
        if acc_option == 5:
            print("You have successfully logged out!")
            print()
            self.initial_option()
            print()
        if acc_option == 0:
            print("Bye!")
            self.close_db()

    def luhn_algorithm(self, verify_card, check):
        """Function to validate card no based on Luhn Algorithm"""
        if check == 0:
            list_of_digits = [2 * int(verify_card[i]) if i % 2 == 0 else int(verify_card[i])
                              for i in range(len(verify_card))]
            check_digit = self.get_check_digit(list_of_digits)
            return check_digit

        elif check == 1:
            list_of_digits = [2 * int(verify_card[i]) if i % 2 == 0 else int(verify_card[i])
                              for i in range(len(verify_card) - 1)]
            check_digit = str(self.get_check_digit(list_of_digits))
            if check_digit == verify_card[-1]:
                return True
            return False

    @staticmethod
    def get_check_digit(digits_list):
        """Function to get check digit of a card"""
        digit_sum = 0
        for num in digits_list:
            if num < 10:
                digit_sum += num
            else:
                digit_sum += (num % 10) + (num // 10)

        if digit_sum % 10 == 0:
            return 0
        else:
            return (digit_sum // 10 + 1) * 10 - digit_sum

    def get_exist_cards(self):
        """Function to get list of existing cards"""
        self.c.execute('''SELECT number FROM card''')
        exist_cards = self.c.fetchall()
        exist_cards = [cards[0] for cards in exist_cards]
        return exist_cards

    def get_pin(self, cardno):
        """Function to get pin for entered card no"""
        self.c.execute('''SELECT pin FROM card WHERE number=?''', (cardno,))
        pin = self.c.fetchone()[0]
        return pin

    def get_balance(self, cardno):
        """Function to get balance for card no"""
        self.c.execute('''SELECT balance FROM card WHERE number=?''', (cardno,))
        bal = self.c.fetchone()[0]
        return bal

    def add_income(self):
        """Function to add income to user's account"""
        print("Enter income:")
        inc = int(input())
        cur_bal = self.get_balance(self.card)
        new_bal = cur_bal + inc
        self.c.execute('''UPDATE card SET balance=? WHERE number=?''', (new_bal, self.card))
        self.db.commit()
        print("Income was added!")

    def transfer_amount(self):
        """Function to make amount transfer between accounts"""
        print("Transfer")
        print("Enter card number:")
        to_card = input()
        if not self.luhn_algorithm(to_card, 1):
            print("Probably you made mistake in the card number. Please try again!")
            return None
        elif to_card not in self.get_exist_cards():
            print("Such a card does not exist.")
            return None
        elif to_card == self.card:
            print("You can't transfer money to the same account!")
            return None
        print("Enter how much money you want to transfer:")
        tran_amt = int(input())
        cur_bal = self.get_balance(self.card)
        if cur_bal < tran_amt:
            print("Not enough money!")
            return None
        to_card_bal = self.get_balance(to_card)
        new_bal = cur_bal - tran_amt
        to_card_new_bal = to_card_bal + tran_amt
        self.c.execute('''UPDATE card SET balance=? WHERE number=?''', (new_bal, self.card))
        self.c.execute('''UPDATE card SET balance=? WHERE number=?''', (to_card_new_bal, to_card))
        self.db.commit()
        print("Success!")

    def close_acc(self):
        """Function to close the account permanently"""
        self.c.execute('''DELETE from card WHERE number=?''', (self.card,))
        self.db.commit()
        print("The account has been closed!")

    def close_db(self):
        """Function to terminate the connection object"""
        self.db.close()
        sys.exit()


if __name__ == '__main__':
    Banking()
