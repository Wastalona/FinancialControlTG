from aiogram import Router, types
from aiogram.filters import Command
from datetime import datetime

from handlers import markup
from handlers.settings import check_admin, logic, connector
from handlers.storages import InfoCollection

cmd_router = Router()


@cmd_router.message(Command("start"))
@check_admin
async def command_start_handler(message:  types.Message) -> None:
    logic.commands_stack.clear()
    await message.answer("Main menu", reply_markup=markup.menu)


@cmd_router.message(Command("stats"))
@check_admin
async def statistics(message: types.Message) -> None:
    await message.answer("statistics")


@cmd_router.message(Command(commands=["asneeded", "percent50", "pc50", "main"]))
@check_admin
async def asneeded(message: types.Message) -> None:
    amount, date = connector.get_info("Main")
    await message.answer(f"As Needed\n=== {date} ===\namount: {amount}")


@cmd_router.message(Command(commands=["optional", "percent20", "pc20", "withme"]))
@check_admin
async def optional(message: types.Message) -> None:
    amount, date = connector.get_info("Optional")
    await message.answer(f"Optional\n=== {date} ===\namount: {amount}")


@cmd_router.message(Command(commands=["storage", "percent30", "pc20", "stg"]))
@check_admin
async def storage(message: types.Message) -> None:
    amount, date = connector.get_info("Storage")
    await message.answer(f"Storage\n=== {date} ===\namount: {amount}")


@cmd_router.message(Command(commands=["transaction", "ts"]))
@check_admin
async def transaction(message: types.Message) -> None:
    await message.answer("transaction\nformat: type payment category amount description")


@cmd_router.message(Command(commands=["transfers", "tf"]))
@check_admin
async def transfers(message: types.Message) -> None:
    await message.answer("transfers\nformat:from to amount")


@cmd_router.message(Command(commands=["debts", "list"]))
@check_admin
async def debts(message: types.Message) -> None:
    await message.answer("debts list\nformat: name amount")


@cmd_router.message(Command(commands=["specific", "spec"]))
@check_admin
async def specific_functions(message: types.Message) -> None:
    await message.answer("specific functions")


@cmd_router.message(Command(commands=["newTransaction", "nts"]))
@check_admin
async def new_transaction(message: types.Message) -> None:
    logic.commands_stack.clear()
    await message.answer("Select action", reply_markup=markup.work)


@cmd_router.message(Command("info"))
@check_admin
async def info(message: types.Message) -> None:
    info_coll = logic.collect_info()

    information = f"{datetime.now().ctime()}\n\n=== Balance ===\n\
(50%) As needed: {info_coll.main}р\n\
(20%) Optional: {info_coll.opt}\n\
(30%) Storage: {info_coll.stg}р\n\
Debts: {info_coll.debt}р\n\
=> Total: {sum([info_coll.main, info_coll.opt, info_coll.stg, info_coll.debt])}р\n\n=== {datetime.now().strftime('%B')} report ===\n\
🔺 Income: {info_coll.month_income}р\n🔻Expenses: {info_coll.month_expenses}р\n\
Top expenses: {info_coll.top_name} with {info_coll.top_expenses}р\n=>Total {info_coll.d}р 🔺\n\n\
=== Formats ===\ncash: {info_coll.cash}р\ncard: {info_coll.card}р"

    await message.answer(information)