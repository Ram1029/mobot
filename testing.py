import dotenv
dotenv.load_dotenv('.env')

import os
import asyncio
from cloud.fsm import FiniteStatesStorage, MessageStorage, create_message_storage, get_message_storage

from db.connection import indev_connection

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def main():
    driver, pool = await indev_connection()
    create_message_storage(MessageStorage(pool=pool))

    from mobot.create_bot import create_bot
    bot, dp = create_bot(bot_token=BOT_TOKEN, bot_storage=FiniteStatesStorage(pool=pool))

    print('Запуск longpolling...')
    try:
        await dp.start_polling(bot)
    except:
        await dp.storage.close()
        await get_message_storage().close()

if __name__ == "__main__":
    asyncio.run(main())