import sqlite3
from datetime import datetime

from handlers.storages import *


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance


@singleton
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

    def get_value(self, table: str, column: str, condition: str = "", data: list = []) -> list:
        query = f"SELECT {column} FROM {table} {condition}"
        if len(data) > 0:
            self.cursor.execute(query, data)
        else:
            self.cursor.execute(query)

        return self.cursor.fetchall()

    def add_transfer(self, value: Transfer):
        query = "INSERT INTO `Transfers` (from_account, to_account, amount, transfer_date) VALUES(?, ?, ?, ?)"
        self.cursor.execute(query, value.to_tuple())
        self.connection.commit()

    def add_transaction(self, value: Transaction):
        query = "INSERT INTO `Transactions` (amount, description, category_id, payment_id, account_id, " \
                "transaction_date) VALUES(?, ?, ?, ?, ?, ?)"
        self.cursor.execute(query, value.to_tuple())
        self.connection.commit()

    def update_balance(self, acc_id: int, value: float, date: datetime, action: bool, stg_id: int):
        # action 0 equal expenses, 1 - income
        # storage 1 equal card, 2 equal cash
        self.cursor.execute(f"SELECT amount FROM Accounts WHERE id=?", (acc_id,))
        acc_amount = self.cursor.fetchone()[0]

        self.cursor.execute(f"SELECT amount FROM Storages WHERE id=?", (stg_id,))
        stg_amount = self.cursor.fetchone()[0]

        if action:
            acc_amount += value
            stg_amount += value
        else:
            acc_amount -= value
            stg_amount -= value

        query = f"UPDATE Accounts SET amount=?, lastUpdate=? WHERE id=?"
        self.cursor.execute(query, (acc_amount, date, acc_id))

        query = f"UPDATE Storages SET amount=?, dateOfUpdate=? WHERE id=?"
        self.cursor.execute(query, (stg_amount, date, stg_id))

        self.connection.commit()

    def data_availability(self):
        self.cursor.execute("SELECT COUNT(*) FROM Transactions")
        return self.cursor.fetchone()[0]

    def __del__(self):
        self.connection.close()


__all__ = ["SqliteController"]
