from aiogram import Bot, Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from os import getenv

from bd.storage import MessageRecord
from bd.connections import global_message_storage, global_user_storage

from mobot.phrases import phrases
from mobot.callbacks import messageCallback, message_callback_handler
import mobot.keyboards as kb

router = Router()

message_storage = global_message_storage
user_storage = global_user_storage

main_channel_id = getenv('MAIN_CHANNEL_ID')
main_chat_id = int(getenv('MAIN_CHAT_ID'))
suggestions_topic_id = int(getenv('SUGGESTIONS_TOPIC_ID'))
questions_topic_id = int(getenv('QUESTIONS_TOPIC_ID'))

@messageCallback('cancel')
async def cancel(callback: CallbackQuery, bot: Bot, substract: int):
    await bot.edit_message_reply_markup(message_id=substract, chat_id=callback.from_user.id)
    message_storage.pop(substract, callback.from_user.id)
    return phrases.cancel_text

@messageCallback('send')
async def send(callback: CallbackQuery, bot: Bot, substract: int):
    posting_message: MessageRecord = message_storage.get(substract, callback.from_user.id)
    if not posting_message:
        await bot.answer_callback_query(callback.id, text='missing data')
        return
    bot_message = await bot.copy_message(from_chat_id=posting_message.from_chat, message_id=posting_message.origin_id, chat_id=main_chat_id, message_thread_id=suggestions_topic_id)
    message_storage.pop(substract, callback.from_user.id)
    message_storage.set(MessageRecord(message_id=bot_message.message_id, chat_id=main_chat_id,from_chat=main_chat_id, from_user=callback.from_user.id, type='moderating', origin_id=posting_message.origin_id))
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=phrases.send, callback_data=f'post|{bot_message.message_id}')],
        [InlineKeyboardButton(text=phrases.cancel, callback_data=f'decline|{bot_message.message_id}')]
    ])
    await bot.edit_message_reply_markup(message_id=substract, chat_id=callback.from_user.id)
    await bot.edit_message_reply_markup(chat_id=main_chat_id, message_id=bot_message.message_id, reply_markup=markup)
    return phrases.send_text

@messageCallback('post')
async def post(callback: CallbackQuery, bot: Bot, substract: int):
    moderating_message: MessageRecord = message_storage.get(substract, main_chat_id)
    if not moderating_message:
        await bot.answer_callback_query(callback.id, text='missing data')
        return None
    await bot.copy_message(chat_id=main_channel_id, from_chat_id=moderating_message.from_user, message_id=moderating_message.origin_id)
    await bot.delete_message(chat_id=main_chat_id, message_id=substract)
    message_storage.pop(substract, main_chat_id)
    return phrases.post_text

@messageCallback('decline')
async def decline(callback: CallbackQuery, bot: Bot, substract: int):
    await bot.delete_message(chat_id=main_chat_id, message_id=substract)
    message_storage.pop(substract, main_chat_id)
    return phrases.decline_text

@messageCallback('ask')
async def ask(callback: CallbackQuery, bot: Bot, substract: int):
    enquiring_message: MessageRecord = message_storage.get(substract, callback.from_user.id)
    if not enquiring_message:
        await bot.answer_callback_query(callback.id, text='missing data')
        return
    bot_message = await bot.copy_message(from_chat_id=enquiring_message.from_chat, message_id=enquiring_message.origin_id, chat_id=main_chat_id, message_thread_id=questions_topic_id)
    message_storage.pop(substract, callback.from_user.id)
    message_storage.set(MessageRecord(message_id=bot_message.message_id, chat_id=main_chat_id, from_user=callback.from_user.id, type='question', origin_id=enquiring_message.origin_id))
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=phrases.close, callback_data=f'close|{bot_message.message_id}')]
    ])
    await bot.edit_message_reply_markup(message_id=substract, chat_id=callback.from_user.id)
    await bot.edit_message_reply_markup(chat_id=main_chat_id, message_id=bot_message.message_id, reply_markup=markup)
    return phrases.ask_text

@messageCallback('close')
async def close(callback: CallbackQuery, bot: Bot, substract: int):
    question_message = message_storage.get(substract, main_chat_id)
    if not question_message.answer_id:
        message_storage.pop(substract, main_chat_id)
        await bot.send_message(chat_id=question_message.from_user, text=phrases.closed, reply_to_message_id=question_message.origin_id)
        await bot.delete_message(message_id=question_message.message_id, chat_id=main_chat_id)
        return phrases.close_text
    else:
        await bot.edit_message_reply_markup(chat_id=main_chat_id, message_id=substract)

@router.callback_query()
async def callback_handler(callback: CallbackQuery, bot: Bot):
    is_message_callback = await message_callback_handler(callback, bot)
    if not is_message_callback:
        pass