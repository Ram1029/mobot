from aiogram import Router, Bot
from aiogram.filters import command
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from asyncio import sleep
from os import getenv

from bd.connections import global_message_storage, global_user_storage
from bd.storage import MessageRecord

import mobot.keyboards as kb
from mobot.phrases import phrases

router = Router()

message_storage = global_message_storage
user_storage = global_user_storage

main_channel_id = getenv('MAIN_CHANNEL_ID')
main_chat_id = int(getenv('MAIN_CHAT_ID'))
suggestions_topic_id = int(getenv('SUGGESTIONS_TOPIC_ID'))
questions_topic_id = int(getenv('QUESTIONS_TOPIC_ID'))

@router.message(command.CommandStart())
async def hewo(message: Message, bot: Bot, state: FSMContext):
    jpeg = FSInputFile('media/mochem.jpeg')
    markup = kb.reply_keyboard
    if message.from_user.id in user_storage:
        markup = kb.reply_keyboard_without_subscribtion
    await bot.send_photo(chat_id=message.from_user.id, photo=jpeg, caption=phrases.hello_message, reply_markup=markup)
    await state.clear()

@router.message(command.Command(commands="sites"))
async def sites(message: Message, bot: Bot):
    jpeg = FSInputFile('media/mochem.jpeg')
    await bot.send_photo(chat_id=message.from_user.id, caption=phrases.sites, photo=jpeg)

@router.message(command.Command(commands="cancel"))
async def cancel(message: Message, state: FSMContext):
    await message.reply(phrases.cancel_message)
    await state.clear()

@router.message(command.Command(commands="subscribtion"))
async def subscription(message: Message):
    user_id = message.from_user.id
    user = user_storage.get(user_id)
    if user.subscription:
        text = phrases.user_unsubscribed
        user_storage.subscribe(user_id, False)
    else:
        text = phrases.user_subscribed
        user_storage.subscribe(user_id)
    await message.reply(text=text)

@router.message(command.Command(commands="ban"))
async def ban_user(message: Message, bot: Bot):
    reply = message.reply_to_message
    if reply:
        reply_message = message_storage.get(reply.message_id, main_chat_id)
        if reply_message and reply_message.type in ['moderating','question','answer']:
            user_id = reply_message.from_user
            user_storage.ban(user_id)
            await message.reply(text=phrases.user_banned)
            messages = message_storage.clean(user_id)
            for msg in messages:
                if msg.chat_id == main_chat_id:
                    await bot.delete_message(chat_id=main_chat_id, message_id=msg.message_id)
    await sleep(5)
    await message.delete()

@router.message(command.Command(commands='close'))
async def close(message: Message, bot: Bot):
    if message.reply_to_message:
        reply_id = message.reply_to_message.message_id
        reply_message: MessageRecord = message_storage.get(reply_id, main_chat_id)
        if reply_message and reply_message.type in ['question', 'answer']:
            question, messages = message_storage.close_qna(reply_message.message_id, main_chat_id=main_chat_id)
            await bot.send_message(chat_id=question.from_user, reply_to_message_id=question.origin_id, text=phrases.cool_closed)
            for msg in messages:
                await bot.delete_message(main_chat_id, msg.message_id)
    await sleep(5)
    await message.delete()

@router.message(command.Command(commands='closeall'))
async def closeall(message: Message, bot:  Bot):
    if message.chat.id == main_chat_id:
        questions, messages = message_storage.close_all_qna(main_chat_id=main_chat_id)
        for msg in messages:
            await bot.delete_message(main_chat_id, msg.message_id)
        for question in questions:
            try:
                await bot.send_message(chat_id=question.from_user, reply_to_message_id=question.origin_id, text=phrases.cool_closed)
            except Exception:
                pass
    await sleep(5)
    await message.delete()


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