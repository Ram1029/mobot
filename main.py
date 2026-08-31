import dotenv
dotenv.load_dotenv('.env')

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import os
import asyncio
from aiogram.client.session.aiohttp import AiohttpSession

import bd.connections as bd

from mobot.create_bot import create_bot

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def main():
    bot, dp = create_bot(bot_token=BOT_TOKEN,bot_storage=bd.redis_storage)

    print('Запуск longpolling...')
    try:
        await dp.start_polling(bot)
    except Exception:
        logger.exception("Бот упал с ошибкой")
    finally:
        await dp.storage.close()

if __name__ == "__main__":
    asyncio.run(main())