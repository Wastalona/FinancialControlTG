import asyncio
import logging
import sys
from datetime import datetime
from os import getenv
import re
import sqlite3

from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

import markup
from db_sqlite import *

# Bot settings
TOKEN: str = getenv("FC_TOKEN")

# All handlers should be attached to the Router (or Dispatcher)
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

sql = SqliteController(path="test.db")

commands_stack: list = []
categories_tuple: tuple = ("Salary", "Parttime", "Parents", "Competition",
                    "Investments", "Freelancing", "Food",
                    "Home", "Phone", "Banking", "Internet", "Bills",
                    "Rent", "Gift", "Closing", "Health", "Shopping",
                    "Education", "Transport", "ForYourself")

accounts_id = [
        sql.get_id(table="Accounts", name="Main"),
        sql.get_id(table="Accounts", name="Optional"),
        sql.get_id(table="Accounts", name="Storage")
    ]


def check_admin(func):
    async def wrapper(message):
        if message.from_user.id != 974268069:
            return await message.reply('Access Denied.\nReason: You are not creator.', reply=False)
        return await func(message)

    return wrapper


@dp.message(Command("start"))
@check_admin
async def command_start_handler(message: Message) -> None:
    commands_stack.clear()
    await message.answer("Main menu", reply_markup=markup.menu)


@dp.message(Command("info"))
@check_admin
async def info(message: types.Message) -> None:
    information = f"{datetime.now().ctime()}\n\n=== Balance ===\n\
(50%) As needed: { sql.get_info('Main')}р\n\
(20%) Optional: {sql.get_info('Optional')}\n\
(30%) Storage: {sql.get_info('Storage')}р\n\
Debts: {sql.get}р\n\
=> Total: р\n\n=== {datetime.now().strftime('%B')} report ===\n\
🔺 Income: р\n🔻Expenses: р\nTop expenses: category_name\n=>Total р 🔺\n\n\
=== Formats ===\ncash: р\ncard: р"

    await message.answer(information)


@dp.message(Command("stats"))
@check_admin
async def statistics(message: types.Message) -> None:
    await message.answer("statistics")


@dp.message(Command(commands=["asneeded", "percent50", "pc50", "main"]))
@check_admin
async def asneeded(message: types.Message) -> None:
    amount, date = sql.get_info("Main")
    await message.answer(f"As Needed\n=== {date} ===\namount: {amount}")


@dp.message(Command(commands=["optional", "percent20", "pc20", "withme"]))
@check_admin
async def optional(message: types.Message) -> None:
    amount, date = sql.get_info("Optional")
    await message.answer(f"Optional\n=== {date} ===\namount: {amount}")


@dp.message(Command(commands=["storage", "percent30", "pc20", "stg"]))
@check_admin
async def storage(message: types.Message) -> None:
    amount, date = sql.get_info("Storage")
    await message.answer(f"Storage\n=== {date} ===\namount: {amount}")


@dp.message(Command(commands=["transaction", "ts"]))
@check_admin
async def transaction(message: types.Message) -> None:
    await message.answer("transaction\nformat: type payment category amount description")


@dp.message(Command(commands=["transfers", "tf"]))
@check_admin
async def transfers(message: types.Message) -> None:
    await message.answer("transfers\nformat:from to amount")


@dp.message(Command(commands=["debts", "list"]))
@check_admin
async def debts(message: types.Message) -> None:
    await message.answer("debts list\nformat: name amount")


@dp.message(Command(commands=["specific", "spec"]))
@check_admin
async def specific_functions(message: types.Message) -> None:
    await message.answer("specific functions")


@dp.message(Command(commands=["newTransaction", "nts"]))
@check_admin
async def new_transaction(message: types.Message) -> None:
    commands_stack.clear()
    await message.answer("Select action", reply_markup=markup.work)


@dp.message((F.text.title()).in_(categories_tuple))
@check_admin
async def check_categories(message: types.Message) -> None:
    commands_stack.append(message.text.title())
    await message.answer(f"Enter {commands_stack[1]} expression")


@dp.message(F.text.regexp(r"^(\d+(?:.\d+)?)-(m|o|s)-?(.+)?").as_("data"))
@check_admin
async def check_expenses(message: types.Message):
    record = message.text.split("-")
    data = [*record, *commands_stack]
    data[0] = float(data[0])

    payment = data[-2].title()
    category_id = sql.get_id(table="Categories", name=data[-1], tr_type="expenses")
    payment_id = sql.get_id(table="Storages", name=payment)

    if len(data) == 6:
        desc = data[2]
    else:
        desc = ""

    accs = {"m": accounts_id[0], "o": accounts_id[1], "s": accounts_id[2]}
    transact = Transaction(data[0], desc, category_id, payment_id, accs[data[1]])

    try:
        value = transact
        sql.add_transaction(value)
        sql.update_balance(value.account_id, value.amount, value.transaction_date, False)
        await message.answer("[ - ] Transaction added", reply_markup=markup.menu)
    except sqlite3.OperationalError as er:
        await message.answer(f"{er}")
    finally:
        commands_stack.clear()


@dp.message(F.text.regexp(r"^(\d+(?:.\d+)?)-?(.+)?"))
@check_admin
async def check_income(message: types.Message) -> None:
    record = message.text.split("-")
    data = [*record, *commands_stack]
    data[0] = float(data[0])

    amounts: list = [round(data[0] * 0.5, 2), round(data[0] * 0.2, 2), round(data[0] * 0.3, 2)]
    payment = data[-2].title()
    category_id = sql.get_id(table="Categories", name=data[-1], tr_type="income")
    payment_id = sql.get_id(table="Storages", name=payment)

    if len(data) == 5: desc = data[1]
    else: desc = ""

    transact_list: list = [
        Transaction(amounts[0], desc, category_id, payment_id, accounts_id[0]),
        Transaction(amounts[1], desc, category_id, payment_id, accounts_id[1]),
        Transaction(amounts[2], desc, category_id, payment_id, accounts_id[2])
    ]

    try:
        for i in range(3):
            value = transact_list[i]
            sql.add_transaction(value)
            sql.update_balance(value.account_id, value.amount, value.transaction_date, True)
        await message.answer("[ + ] Transaction added", reply_markup=markup.menu)
    except sqlite3.OperationalError as er:
        await message.answer(f"{er}")
    finally:
        commands_stack.clear()

# Debt
# @dp.message(F.text.regexp(r"^(\d+(?:.\d+)?) ?(.+)?").as_("data"))
# @check_admin
# async def check_categories(message: types.Message, data: list):
#     print(f"[ DEBUG ] {data}")
#     await message.answer("debt was writen")
#
#
# # Transfer
# @dp.message(F.text.regexp(r"^(\d+(?:.\d+)?) ?(.+)?").as_("data"))
# @check_admin
# async def check_categories(message: types.Message, data: list):
#     print(f"[ DEBUG ] {data}")
#     await message.answer("transfer was writen")


@dp.message()
@check_admin
async def check_functions(message: types.Message):
    functions = {
        "as needed": asneeded,
        "optional": optional,
        "storage": storage,
        "transaction": transaction,
        "transfers": transfers,
        "debts": debts,
        "info": info,
        "statistics": statistics,
        "new transaction": new_transaction,
        "menu": command_start_handler,
        "back": new_transaction
    }

    try:
        msg = message.text.lower()
    except TypeError as er:
        await message.answer(f"Sometimes went wrong: Error: {er}")

    if msg in functions:
        await functions[msg](message)

    if msg in ("+ card", "+ cash"):
        commands_stack.append("income")
        commands_stack.append(msg[2:])
        await message.reply("Choose income category", reply_markup=markup.income_categories())
    elif msg in ("- card", "- cash"):
        commands_stack.append("expenses")
        commands_stack.append(msg[2:])
        await message.reply("Choose expenses category", reply_markup=markup.expenses_categories())
    elif msg in ("+ debt", "- debt"):
        # add_debt(msg.split(" ")[0])
        await message.reply("Enter debt expression")
    elif msg == "transfer":
        # add_transfer(msg.split(" ")[0])
        await message.reply("Enter transfer expression")


# await message.reply("Unknown command")


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
