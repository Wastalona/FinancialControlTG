from handlers.db_sqlite import *
from handlers.backend import Backend

connector = SqliteController(path="test.db")
logic = Backend(connector)


def check_admin(func):
    async def wrapper(message):
        if message.from_user.id != 974268069:
            return await message.reply('Access Denied.\nReason: You are not creator.', reply=False)
        return await func(message)

    return wrapper
