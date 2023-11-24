import sqlite3
from aiogram import Router, types, F

from handlers import markup
from handlers.node import check_admin, logic, connector
from handlers.storages import *
from handlers.commands import (
    command_start_handler, statistics, asneeded, optional,
    storage, transactions_out, transfers, debts, specific_functions,
    new_transaction, info)

messages_router = Router()


@messages_router.message((F.text.title()).in_(logic.categories_tuple))
@check_admin
async def check_categories(message: types.Message) -> None:
    logic.commands_stack.append(message.text.title())
    await message.answer(f"Enter {logic.commands_stack[1]} expression")


@messages_router.message(F.text.regexp(r"^(\d+(?:.\d+)?)-(m|o|s)-?(.+)?"))
@check_admin
async def check_expenses(message: types.Message):
    db_answer = logic.process_transaction(message.text, "expenses")
    await message.answer(db_answer, reply_markup=markup.menu)


@messages_router.message(F.text.regexp(r"^(\d+(?:.\d+)?)-?(.+)?"))
@check_admin
async def check_income(message: types.Message) -> None:
    db_answer = logic.process_transaction(message.text, "income")
    await message.answer(db_answer, reply_markup=markup.menu)

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
@messages_router.message(F.text.regexp(r"^(m|s|o)-(m|s|o)-(\d+(?:.\d+)?)-(cd|cs)"))
@check_admin
async def check_categories(message: types.Message):
    record = message.text.lower().split("-")
    stg_from, stg_to = (1, 2) if record[3] == "cd" else (2, 1)

    transfer = Transfer(logic.accounts_id[record[0]], logic.accounts_id[record[1]], float(record[2]))

    try:
        connector.add_transfer(transfer)
        connector.update_balance(transfer.from_account, transfer.amount, transfer.transfer_date, False, stg_from)
        connector.update_balance(transfer.to_account, transfer.amount, transfer.transfer_date, True, stg_to)
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
        "transaction": transactions_out,
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
