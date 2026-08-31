from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from handlers.callback import router as callback
from handlers.commands import router as commands
from handlers.message import router as message

from aiogram.client.session.aiohttp import AiohttpSession

def create_bot(bot_token, bot_storage = MemoryStorage(), session: AiohttpSession = None):
    mobot = Bot(token=bot_token, session=session)
    dp = Dispatcher(storage=bot_storage)
    dp.include_routers(callback, commands, message)
    return mobot, dp