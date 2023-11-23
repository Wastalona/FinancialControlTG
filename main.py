import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from handlers import commands, messages


TOKEN = getenv("FC_TOKEN")


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
