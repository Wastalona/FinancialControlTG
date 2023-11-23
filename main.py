import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from handlers.db_sqlite import *
from handlers.backend import Backend
from handlers import commands, messages

# Bot settings
TOKEN = getenv("FC_TOKEN")

connector = SqliteController(path="test.db")
logic = Backend(connector)


def check_admin(func):
    async def wrapper(message):
        if message.from_user.id != 974268069:
            return await message.reply('Access Denied.\nReason: You are not creator.', reply=False)
        return await func(message)

    return wrapper


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    dp.include_routers(
        commands.cmd_router,
        messages.messages_router
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
