import os
import json
import asyncio
from aiogram import types

from db.connection import create_connection
from mobot.create_bot import create_bot
from cloud.fss import FiniteStatesStorage

# Lockbox-секреты подтягиваются как переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

driver, pool = asyncio.run(create_connection())

bot, dp = create_bot(bot_token=BOT_TOKEN, bot_storage=FiniteStatesStorage(pool))

# Регистрируешь свои хэндлеры
# @dp.message(...)
# async def handle_message(msg: types.Message): ...

async def handler(event, context):
    """Точка входа для Cloud Functions."""
    try:
        update = types.Update(**json.loads(event['body']))
        await dp.feed_update(bot, update)
        return {
            'statusCode': 200,
            'body': json.dumps({'ok': True})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }