import sqlite3
from datetime import datetime
from dataclasses import dataclass


@dataclass
class Transaction:
    amount: float
    description: str
    category_id: int
    payment_id: int
    account_id: int
    transaction_date: datetime = datetime.utcnow()

    def to_tuple(self):
        return (
            self.amount,
            self.description,
            self.category_id,
            self.payment_id,
            self.account_id,
            self.transaction_date,
        )


@dataclass
class Transfer:
    from_account: int
    to_account: int
    amount: float
    transfer_date: datetime = datetime.utcnow()

    def to_tuple(self):
        return (
            self.from_account,
            self.to_account,
            self.amount,
            self.transfer_date,
        )


class SqliteController:
    def __init__(self, *, path="budget.db"):
        try:
            self.connection = sqlite3.connect(path)
            self.cursor = self.connection.cursor()
        except sqlite3.Error as er:
            print(f"[ DEBUG ] Error:{er}")

    def get_id(self, *, table: str, name: str, tr_type: str = "") -> int:
        column_name = "name"
        if table == "Storages":
            column_name = "storageName"
        elif table == "Accounts":
            column_name = "accountName"

        query = f"SELECT id FROM {table} WHERE {column_name} = ?"
        params = [name]

        if tr_type:
            query += " AND transaction_type = ?"
            params.append(tr_type)

        try:
            self.cursor.execute(query, tuple(params))
            category_id = self.cursor.fetchone()
            return int(category_id[0]) if category_id else 0
        except sqlite3.OperationalError as er:
            print(f"[ DEBUG ] {er}")
            return 0

    def get_info(self, acc_name: str) -> list:
        query = f"SELECT amount, lastUpdate FROM Accounts WHERE accountName=?"
        try:
            self.cursor.execute(query, (acc_name,))
            return self.cursor.fetchall()[0]
        except sqlite3.OperationalError:
            return ["None", "None"]


    def add_transfer(self, value: Transfer):
        query = "INSERT INTO `Transfers` (from_account, to_account, amount, transfer_date) VALUES(?, ?, ?, ?)"
        self.cursor.execute(query, value.to_tuple())
        self.connection.commit()

    def add_transaction(self, value: Transaction):
        query = "INSERT INTO `Transactions` (amount, description, category_id, payment_id, account_id, transaction_date) VALUES(?, ?, ?, ?, ?, ?)"
        self.cursor.execute(query, value.to_tuple())
        self.connection.commit()

    def update_balance(self, acc_id: int, value: float, date: datetime, action: bool):
        # action 0 equal expenses, 1 - income
        self.cursor.execute(f"SELECT amount FROM Accounts WHERE id={acc_id}")
        old_amount = self.cursor.fetchone()[0]

        if action:
            value = round(old_amount+value, 2)
        else:
            value = round(old_amount-value, 2)

        query = f"UPDATE Accounts SET amount=?, lastUpdate=? WHERE id={acc_id}"
        self.cursor.execute(query, (value, date))
        self.connection.commit()

    def __del__(self):
        self.connection.close()


__all__ = ["Transaction", "SqliteController", "Transfer"]