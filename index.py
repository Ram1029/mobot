import os
import json
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from ydb import Driver, SessionPool
from ydb.iam import ServiceAccountCredentials
from mobot.create_bot import create_bot

# Lockbox-секреты подтягиваются как переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
YDB_ENDPOINT = os.getenv("YDB_ENDPOINT")
YDB_DATABASE = os.getenv("YDB_DATABASE")

# Глобальный пул соединений YDB (создаётся один раз при холодном старте)
ydb_driver = Driver(
    endpoint=YDB_ENDPOINT,
    database=YDB_DATABASE,
    credentials=ServiceAccountCredentials(),
)
ydb_pool = SessionPool(ydb_driver, size=5)

bot, dp = create_bot(bot_token=BOT_TOKEN)

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