from typing import *
from aiogram import Bot
from aiogram.types import CallbackQuery

callbacks = {}
def messageCallback(callback_type):
    """Добавляет функцию в местный роутер message callbacks, в качестве аргумента принимает тип message callback. Фукнкция должна принимать аргументы CallbackQuery, Bot и message.id"""
    def decorator(func):
        global callbacks
        callbacks[callback_type] = func
    return decorator

async def message_callback_handler(callback: CallbackQuery, bot: Bot):
    data = callback.data.split('|')
    if len(data) == 2:
        callback_type, substract = data
        if callback_type in callbacks:
            text = await callbacks[callback_type](callback, bot, substract)
            if text:
                await bot.answer_callback_query(callback.id, text=text)
        else:
            await bot.answer_callback_query(callback.id)
        return True
    return False