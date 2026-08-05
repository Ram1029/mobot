from aiogram import Router, Bot
from aiogram.types import Message, MessageEntity, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram import F

from bd.connections import global_message_storage, global_user_storage
from bd.storage import MessageRecord

from mobot.fsm import MessageStates
from mobot.phrases import phrases
import mobot.keyboards as kb

router = Router()

message_storage = global_message_storage
user_storage = global_user_storage

@router.message(F.text, default_state)
async def message_handler(message: Message, bot: Bot, state: FSMContext):
    chat_id = message.chat.id

    if message.text == phrases.post_message:
        await state.set_state(MessageStates.posting)
        await bot.send_message(chat_id=chat_id, text=phrases.send_message)
    if message.text == phrases.make_question:
        await state.set_state(MessageStates.enquiring)
        await bot.send_message(chat_id=chat_id, text=phrases.make_question_message)
    if message.text == phrases.subscribe:
        user_storage.subscribe(message.from_user.id)
        markup = kb.reply_keyboard_without_subscribtion
        await message.reply(text=phrases.subscribe_text, reply_markup=markup)

    match message.entities:
        case [MessageEntity(offset=0, type='custom_emoji', custom_emoji_id=emoji)]:
            await bot.send_message(chat_id=chat_id, text=f'Custom emoji id: {emoji}')
#/
@router.message(MessageStates.posting, ~F.text.startswith('/'))
async def posting(message: Message, bot: Bot, state: FSMContext):
    user_id = message.from_user.id
    chat_id = message.chat.id

    bot_message = await bot.copy_message(message_id=message.message_id, chat_id=chat_id, from_chat_id=chat_id)
    message_storage.set(MessageRecord(message_id=bot_message.message_id, chat_id=chat_id, from_user=user_id, type='posting', origin_id=message.message_id))
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=phrases.send, callback_data=f'send|{bot_message.message_id}')],
        [InlineKeyboardButton(text=phrases.cancel, callback_data=f'cancel|{bot_message.message_id}')]
    ])
    await state.clear()
    await bot.edit_message_reply_markup(chat_id=chat_id, message_id=bot_message.message_id, reply_markup=markup)

@router.message(MessageStates.enquiring, ~F.text.startswith('/'))
async def enquiring(message: Message, bot: Bot, state: FSMContext):
    user_id = message.from_user.id
    chat_id = message.chat.id

    bot_message = await bot.copy_message(message_id=message.message_id, chat_id=chat_id, from_chat_id=chat_id)
    message_storage.set(MessageRecord(message_id=bot_message.message_id, chat_id=user_id, from_user=user_id, type='enquiring', origin_id=message.message_id))
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=phrases.ask, callback_data=f'ask|{bot_message.message_id}')],
        [InlineKeyboardButton(text=phrases.cancel, callback_data=f'cancel|{bot_message.message_id}')]
    ])
    await state.clear()
    await bot.edit_message_reply_markup(chat_id=chat_id, message_id=bot_message.message_id, reply_markup=markup)