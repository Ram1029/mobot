from aiogram import Router, Bot
from aiogram.types import Message, MessageEntity, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram import F
from os import getenv

from bd.connections import global_message_storage, global_user_storage
from bd.storage import MessageRecord

from mobot.fsm import MessageStates
from mobot.phrases import phrases
import mobot.keyboards as kb

router = Router()

message_storage = global_message_storage
user_storage = global_user_storage

main_channel_id = getenv('MAIN_CHANNEL_ID')
main_chat_id = int(getenv('MAIN_CHAT_ID'))
suggestions_topic_id = int(getenv('SUGGESTIONS_TOPIC_ID'))
questions_topic_id = int(getenv('QUESTIONS_TOPIC_ID'))
announcement_topic_id = int(getenv('ANNOUNCEMENTS_TOPIC_ID'))

async def replying(message: Message, bot: Bot):
    reply_id = message.reply_to_message.message_id
    reply_message: MessageRecord = message_storage.get(reply_id, message.reply_to_message.chat.id)
    if reply_message:
        if reply_message.type == 'question':
            answering = await bot.copy_message(chat_id=reply_message.from_user, from_chat_id=main_chat_id, message_id=message.message_id, reply_to_message_id=reply_message.origin_id)
            if message.reply_to_message.reply_markup:
                await bot.edit_message_reply_markup(chat_id=main_chat_id, message_id=reply_id)
            message_storage.set(MessageRecord(message_id=message.message_id, chat_id=main_chat_id, from_user=reply_message.from_user, origin_id=message.message_id, type='answer', answer_id=reply_message.answer_id))
            message_storage.set(MessageRecord(message_id=answering.message_id, chat_id=reply_message.from_user, from_user=reply_message.from_user, origin_id=message.message_id, type='answering', from_chat=main_chat_id, answer_id=reply_message.answer_id))
        if reply_message.type == 'answering':
            question = await bot.copy_message(chat_id=main_chat_id, message_thread_id=questions_topic_id, from_chat_id=reply_message.chat_id, message_id=message.message_id, reply_to_message_id=reply_message.origin_id)
            message_storage.set(MessageRecord(message_id=question.message_id, chat_id=main_chat_id, from_user=message.from_user.id, origin_id=message.message_id, answer_id=reply_message.answer_id, type='question'))
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=phrases.close, callback_data=f'close|{question.message_id}')]
            ])
            await bot.edit_message_reply_markup(chat_id=main_chat_id, message_id=question.message_id, reply_markup=markup)
            await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

@router.message(F.text, default_state)
async def message_handler(message: Message, bot: Bot, state: FSMContext):
    chat_id = message.chat.id

    blocked = user_storage.get(message.from_user.id).banned

    if not blocked:

        if message.text == phrases.post_message:
            await state.set_state(MessageStates.posting)
            await bot.send_message(chat_id=chat_id, text=phrases.send_message)
        if message.text == phrases.make_question:
            await state.set_state(MessageStates.enquiring)
            await bot.send_message(chat_id=chat_id, text=phrases.make_question_message)

    else:
        if message.text in [phrases.post_message, phrases.make_question]:
            await message.answer(phrases.banned)

    if message.text == phrases.subscribe:
        user_storage.subscribe(message.from_user.id)
        markup = kb.reply_keyboard_without_subscribtion
        await message.reply(text=phrases.subscribe_text, reply_markup=markup)

    if message.reply_to_message:
        await replying(message, bot)

    if message.chat.id == main_chat_id:
        if message.message_thread_id == announcement_topic_id:
            announcement = await bot.copy_message(chat_id=main_chat_id, from_chat_id=main_chat_id, message_id=message.message_id, message_thread_id=announcement_topic_id)
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=phrases.post, callback_data=f'announcement|{announcement.message_id}')],
                [InlineKeyboardButton(text=phrases.cancel, callback_data=f'acancel|{announcement.message_id}')]
            ])
            await bot.edit_message_reply_markup(chat_id=main_chat_id, message_id=announcement.message_id, reply_markup=markup)
            await message.delete()

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