import sqlite3

from handlers.storages import *


class Backend:
    def __init__(self, connector):
        self.sql = connector

        self.categories_tuple: tuple = (
            "Salary", "Parttime", "Parents", "Competition",
            "Investments", "Freelancing", "Food",
            "Home", "Phone", "Banking", "Internet", "Bills",
            "Rent", "Gift", "Closing", "Health", "Shopping",
            "Education", "Transport", "ForYourself"
        )

        self.accounts_id = {
            "m": self.sql.get_id(table="Accounts", name="Main"),
            "o": self.sql.get_id(table="Accounts", name="Optional"),
            "s": self.sql.get_id(table="Accounts", name="Storage")
        }

        self.commands_stack = []

    @staticmethod
    def tuples_inlist(tuples: list, values_type: str = "float") -> list:
        """A list with tuples is converted to a list with the desired type"""
        if values_type == "float":
            return [float(x[0]) for x in tuples]
        elif values_type == "int":
            return [int(x[0]) for x in tuples]
        elif values_type == "none":
            return [x[0] for x in tuples]

    def collect_info(self) -> InfoCollection:
        main, opt, stg = [self.sql.get_info(index)[0] for index in ["Main", "Optional", "Storage"]]
        debt = self.sql.get_value("Debts", "SUM(amount)")[0][0]

        month_expenses, month_income, d, top_expenses, top_name = [0, 0, 0, 0, "All"]

        if self.sql.data_availability() != 0:
            category_ex = ', '.join([str(i) for i in range(16, 24)])
            month_expenses = self.sql.get_value(
                "Transactions", "SUM(amount)", f"WHERE category_id NOT IN ({category_ex})")[0][0]

            category_in = ', '.join(str(i) for i in range(1, 16) if i not in range(16, 24))
            month_income = self.sql.get_value(
                "Transactions", "SUM(amount)", f"WHERE category_id NOT IN ({category_in})")[0][0]

            if month_expenses != None and month_income != None:
                d = month_income - month_expenses
                top_expenses, category_id = self.sql.get_value(
                    "Transactions", "MAX(amount), category_id", f"WHERE category_id NOT IN ({category_ex})")[0]

                top_name = self.sql.get_value("Categories", "name", "WHERE id=?", [category_id])[0][0]
            elif month_expenses != None:
                d = -month_expenses
                top_expenses, category_id = self.sql.get_value(
                    "Transactions", "MAX(amount), category_id", f"WHERE category_id NOT IN ({category_ex})")[0]

                top_name = self.sql.get_value("Categories", "name", "WHERE id=?", [category_id])[0][0]
            elif month_income != None:
                d = month_income

        card, cash = self.tuples_inlist(self.sql.get_value("Storages", "amount"))

        return InfoCollection(main, opt, stg, debt, month_expenses, month_income, d, top_expenses, top_name, cash, card)

    def process_transaction(self, message: str, tr_type: str) -> str:
        record = message.split("-")
        data = [*record, *self.commands_stack]
        data[0] = round(float(data[0]), 2)

        payment = data[-2].title()
        category_id = self.sql.get_id(table="Categories", name=data[-1], tr_type=tr_type)
        payment_id = self.sql.get_id(table="Storages", name=payment)
        stg = 2 if payment == "Cash" else 1

        if len(data) == 5 and tr_type == "income":
            desc = data[1]
        elif len(data) == 6 and tr_type == "expenses":
            desc = data[2]
        else:
            desc = ""

        transact_list = []
        if tr_type == "income":
            amounts = [round(data[0] * 0.5, 2), round(data[0] * 0.2, 2), round(data[0] * 0.3, 2)]
            accounts = ["m", "o", "s"]
            for i, acc in enumerate(accounts):
                transact_list.append(Transaction(amounts[i], desc, category_id, payment_id, self.accounts_id[acc]))
        else:
            transact = Transaction(data[0], desc, category_id, payment_id, self.accounts_id[data[1]])
            transact_list = [transact]

        try:
            for value in transact_list:
                self.sql.add_transaction(value)
                self.sql.update_balance(value.account_id, value.amount, value.transaction_date, tr_type == "income", stg)
            return "[+] Transaction added"
        except sqlite3.OperationalError as er:
            return f"Error: {er}"
        finally:
            self.commands_stack.clear()

    def get_transaction(self, *, out_format: str = "list"):
        # str, list
        tr = self.sql.get_value("Transactions", "*", "LIMIT 7")
        out = []
        for transact in tr:
            msg = ""
            id, amount, desc, cat, pay, acc, date = transact
            cat = self.sql.get_value("Categories", "name", "WHERE id=?", [cat])[0][0]
            pay = self.sql.get_value("Storages", "storageName", "WHERE id=?", [pay])[0][0]
            acc = self.sql.get_value("Accounts", "accountName", "WHERE id=?", [acc])[0][0]

            msg = f"| {acc[0]} | {cat} {amount} {pay} {date[:10]}\n"
            if len(desc) > 0:
                msg += f"| {acc[0]}+ {desc}\n"

            out.append(msg)
            msg = ""

        if out_format == "str":
            return "".join(out)

        return out

    def push_in_db(self, message: str, _type: str):
        ...

    def __del__(self):
        ...

