from aiogram import Router, Bot
from aiogram.filters import command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from bd.connections import global_message_storage, global_user_storage

import mobot.keyboards as kb
from mobot.phrases import phrases

router = Router()

message_storage = global_message_storage
user_storage = global_user_storage

@router.message(command.CommandStart())
async def hewo(message: Message, bot: Bot, state: FSMContext):
    markup = kb.reply_keyboard
    inline_markup = kb.start_inline_keyboard
    if message.from_user.id in user_storage:
        markup = kb.reply_keyboard_without_subscribtion
        inline_markup = kb.start_inline_keyboard_without_subscribtion
    start_message_id = await bot.send_message(chat_id=message.chat.id, text=phrases.hello_message, reply_markup=markup, inline_keyboard=inline_markup)
    await state.set_data({
        'start_message_id': start_message_id
    })

@router.message(command.Command(commands="cancel"))
async def cancel(message: Message, state: FSMContext):
    await message.reply(phrases.cancel_message)
    await state.clear()

@router.message(command.Command(commands="subscription"))
async def subscription(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user = user_storage.get(user_id)
    if user.subscription:
        text = phrases.user_unsibscribed
        user_storage.subscribe(user_id, False)
    else:
        text = phrases.user_subscribed
        user_storage.subscribe(user_id)
    message.reply(text=text)

@router.message(command.Command(commands="ban"))
async def ban_user(message: Message, bot: Bot):
    reply = message.reply_to_message
    if reply:
        reply_message = message_storage.get(reply.message_id)
        if reply_message.type in ['moderating','question']:
            user_id = reply_message.from_user
            user_storage.ban(user_id)
            await message.reply(text=phrases.user_banned)

@router.message(command.Command(commands="get_topic"))
async def get_channel_topic_id(message: Message, bot: Bot):
    if message.chat.is_forum:
        topic_id = message.message_thread_id
    if topic_id:
        await bot.send_message(chat_id=message.chat.id, message_thread_id=topic_id, receiver_user_id=message.from_user.id, text=f'current chat id: `{message.chat.id}`', parse_mode='MarkdownV2')
        await bot.send_message(chat_id=message.chat.id, message_thread_id=topic_id, receiver_user_id=message.from_user.id, text=f'current message thread \(topic\) id: `{topic_id}`', parse_mode='MarkdownV2')
    else:
        await bot.send_message(chat_id=message.chat.id, receiver_user_id=message.from_user.id, text=phrases.not_a_topic)
        await bot.send_message(chat_id=message.chat.id, receiver_user_id=message.from_user.id, text=f'current chat id: `{message.chat.id}`', parse_mode='MarkdownV2')
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)