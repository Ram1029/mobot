from aiogram import Router, Bot
from aiogram.filters import command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext

from mobot.phrases import phrases
from mobot.fsm import FiniteStates

router = Router()

@router.message(command.CommandStart())
async def hewo(message: Message, bot: Bot, state: FSMContext):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text=phrases.post_message, icon_custom_emoji_id='5282857993677860851')]
    ])
    await state.set_state(FiniteStates.default)
    await bot.send_message(chat_id=message.chat.id, text=phrases.hello_message, reply_markup=markup)

@router.message(command.Command(commands="cancel"))
async def cancel(message: Message, state: FSMContext):
    await message.reply(phrases.cancel_message)
    await state.set_state(FiniteStates.default)

@router.message(command.Command(commands="ban"))
async def ban_user(message: Message):
    if message.reply_to_message:
        pass

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