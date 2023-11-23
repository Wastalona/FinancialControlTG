import sqlite3
from aiogram import Router, types, F

from handlers import markup
from main import check_admin, logic, connector
from storages import *
from commands import (
    command_start_handler, statistics, asneeded, optional,
    storage, transaction, transfers, debts, specific_functions,
    new_transaction, info)

messages_router = Router()


@messages_router.message((F.text.title()).in_(logic.categories_tuple))
@check_admin
async def check_categories(message: types.Message) -> None:
    logic.commands_stack.append(message.text.title())
    await message.answer(f"Enter {logic.commands_stack[1]} expression")


@messages_router.message(F.text.regexp(r"^(\d+(?:.\d+)?)-(m|o|s)-?(.+)?").as_("data"))
@check_admin
async def check_expenses(message: types.Message):
    record = message.text.split("-")
    data = [*record, *logic.commands_stack]
    data[0] = float(data[0])

    payment = data[-2].title()
    category_id = connector.get_id(table="Categories", name=data[-1], tr_type="expenses")
    payment_id = connector.get_id(table="Storages", name=payment)

    if len(data) == 6:
        desc = data[2]
    else:
        desc = ""

    transact = Transaction(data[0], desc, category_id, payment_id, logic.accounts_id[data[1]])

    try:
        value = transact
        connector.add_transaction(value)
        connector.update_balance(value.account_id, value.amount, value.transaction_date, False)
        await message.answer("[ - ] Transaction added", reply_markup=markup.menu)
    except sqlite3.OperationalError as er:
        await message.answer(f"{er}")
    finally:
        logic.commands_stack.clear()


@messages_router.message(F.text.regexp(r"^(\d+(?:.\d+)?)-?(.+)?"))
@check_admin
async def check_income(message: types.Message) -> None:
    record = message.text.split("-")
    data = [*record, *logic.commands_stack]
    data[0] = float(data[0])

    amounts: list = [round(data[0] * 0.5, 2), round(data[0] * 0.2, 2), round(data[0] * 0.3, 2)]
    payment = data[-2].title()
    category_id = connector.get_id(table="Categories", name=data[-1], tr_type="income")
    payment_id = connector.get_id(table="Storages", name=payment)

    if len(data) == 5: desc = data[1]
    else: desc = ""

    transact_list: list = [
        Transaction(amounts[0], desc, category_id, payment_id, logic.accounts_id["m"]),
        Transaction(amounts[1], desc, category_id, payment_id, logic.accounts_id["o"]),
        Transaction(amounts[2], desc, category_id, payment_id, logic.accounts_id["s"])
    ]

    try:
        for i in range(3):
            value = transact_list[i]
            connector.add_transaction(value)
            connector.update_balance(value.account_id, value.amount, value.transaction_date, True)
        await message.answer("[ + ] Transaction added", reply_markup=markup.menu)
    except sqlite3.OperationalError as er:
        await message.answer(f"{er}")
    finally:
        logic.commands_stack.clear()

# Debt
# @dp.message(F.text.regexp(r"^(\w+)-(\d+(?:.\d+)?)-(\d+(?:.\d+)?)-(.+)"))
# @check_admin
# async def check_categories(message: types.Message):
#     record: list = message.text.split("-")
#     data: list = [*record, *commands_stack]
#
#     commission: int = round(float(data[1]) - float(data[2]), 2)
#     payment: str = data[-2].title()
#     category_id: int = connector.get_id(table="Categories", name="Debt", tr_type="expenses")
#     category_id_com: int = connector.get_id(table="Categories", name="Commission", tr_type="expenses")
#     payment_id: int = connector.get_id(table="Storages", name=payment)
#
#     transact = Transaction(data[2], data[0], category_id, payment_id, accounts_id[1])
#     transact_com = Transaction(commission, data[0], category_id_com, payment_id, accounts_id[1])
#
#     try:
#         connector.add_transaction(transact)
#         connector.add_transaction(transact_com)
#         connector.update_balance(transact.account_id, transact.amount, transact.transaction_date, False)
#         connector.update_balance(transact_com.account_id, transact_com.amount, transact_com.transaction_date, False)
#         await message.answer("[ D ] Transaction added", reply_markup=markup.menu)
#     except sqlite3.OperationalError as er:
#         await message.answer(f"{er}")
#     finally:
#         commands_stack.clear()

# Transfer
@messages_router.message(F.text.regexp(r"^(m|s|o)-(m|s|o)-(\d+(?:.\d+)?)"))
@check_admin
async def check_categories(message: types.Message):
    record = message.text.lower().split("-")

    transfer = Transfer(logic.accounts_id[record[0]], logic.accounts_id[record[1]], float(record[2]))

    try:
        connector.add_transfer(transfer)
        connector.update_balance(transfer.from_account, transfer.amount, transfer.transfer_date, False)
        connector.update_balance(transfer.to_account, transfer.amount, transfer.transfer_date, True)
        await message.answer("[ ~ ] Transfer added", reply_markup=markup.menu)
    except sqlite3.OperationalError as er:
        await message.answer(f"{er}")
    finally:
        logic.commands_stack.clear()


@messages_router.message()
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
        logic.commands_stack.append("income")
        logic.commands_stack.append(msg[2:])
        await message.reply("Choose income category", reply_markup=markup.income_categories())
    elif msg in ("- card", "- cash"):
        logic.commands_stack.append("expenses")
        logic.commands_stack.append(msg[2:])
        await message.reply("Choose expenses category", reply_markup=markup.expenses_categories())
    elif msg in ("+ debt", "- debt"):
        logic.commands_stack.append(msg[0])
        await message.reply("Enter debt expression")
    elif msg == "transfer":
        # add_transfer(msg.split(" ")[0])
        await message.reply("Enter transfer expression")