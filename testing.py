import dotenv
dotenv.load_dotenv('.env')

import os
import asyncio
from cloud.fss import FiniteStatesStorage

from db.connection import indev_connection
from mobot.create_bot import create_bot

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def main():
    driver, pool = await indev_connection()
    bot, dp = create_bot(bot_token=BOT_TOKEN, bot_storage=FiniteStatesStorage(pool=pool))
    print('Запуск longpolling...')
    try:
        await dp.start_polling(bot)
    except:
        await dp.storage.close()

if __name__ == "__main__":
    asyncio.run(main())