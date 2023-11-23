from handlers.storages import InfoCollection


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

    def collect_info(self) -> list:
        main = self.sql.get_info('Main')[0]
        opt = self.sql.get_info('Optional')[0]
        stg = self.sql.get_info('Storage')[0]
        debt = self.sql.get_value("Debts", "SUM(amount)")[0][0]

        category_ex = ', '.join([str(i) for i in range(16, 24)])
        month_expenses = self.sql.get_value("Transactions", "SUM(amount)", f"WHERE category_id NOT IN ({category_ex})")[0][0]
        category_in = ', '.join(str(i) for i in range(1, 16) if i not in range(16, 24))
        month_income = self.sql.get_value("Transactions", "SUM(amount)", f"WHERE category_id NOT IN ({category_in})")[0][0]

        d = month_income - month_expenses
        top_expenses, category_id = \
        self.sql.get_value("Transactions", "MAX(amount), category_id", f"WHERE category_id NOT IN ({category_ex})")[0]
        top_name = self.sql.get_value("Categories", "name", "WHERE id=?", [category_id])[0][0]

        cash, card = self.tuples_inlist(self.sql.get_value("Storages", "amount"))

        return InfoCollection(main, opt, stg, debt, month_expenses, month_income, d, top_expenses, top_name, cash, card)

    def push_in_db(self):
        ...
        # record = message.text.split("-")
        # data = [*record, *commands_stack]
        # data[0] = float(data[0])
        #
        # payment = data[-2].title()
        # category_id = sql.get_id(table="Categories", name=data[-1], tr_type="expenses")
        # payment_id = sql.get_id(table="Storages", name=payment)
        #
        # if len(data) == 6:
        #     desc = data[2]
        # else:
        #     desc = ""
        #
        # transact = Transaction(data[0], desc, category_id, payment_id, accs[data[1]])
        #
        # try:
        #     value = transact
        #     sql.add_transaction(value)
        #     sql.update_balance(value.account_id, value.amount, value.transaction_date, False)
        #     await message.answer("[ - ] Transaction added", reply_markup=markup.menu)
        # except sqlite3.OperationalError as er:
        #     await message.answer(f"{er}")
        # finally:
        #     commands_stack.clear()


    def __del__(self):
        ...

