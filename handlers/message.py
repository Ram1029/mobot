from aiogram import Router, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, MessageEntity
from aiogram.fsm.context import FSMContext
from aiogram import F

from mobot.phrases import phrases
from mobot.fsm import FiniteStates
#from cloud.fsm import MessageRecord, get_message_storage
from bd.connections import global_message_storage
from bd.storage import MessageRecord

router = Router()

message_storage = global_message_storage

@router.message(FiniteStates.default, F.text)
async def message_handler(message: Message, bot: Bot, state: FSMContext):
    chat_id = message.chat.id

    if message.text == phrases.post_message:
        await state.set_state(FiniteStates.posting)
        await bot.send_message(chat_id=chat_id, text=phrases.send_message)

    match message.entities:
        case [MessageEntity(offset=0, type='custom_emoji', custom_emoji_id=emoji)]:
            await bot.send_message(chat_id=chat_id, text=f'Custom emoji id: {emoji}')
#/
@router.message(FiniteStates.posting, ~F.text.startswith('/'))
async def posting(message: Message, bot: Bot, state: FSMContext):
    user_id = message.from_user.id
    chat_id = message.chat.id

    bot_message = await bot.copy_message(message_id=message.message_id, chat_id=chat_id, from_chat_id=chat_id)
    message_storage.set(MessageRecord(message_id=bot_message.message_id, from_user=user_id, type='posting', origin=message.message_id))
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=phrases.send, callback_data=f'send|{bot_message.message_id}')],
        [InlineKeyboardButton(text=phrases.cancel, callback_data=f'cancel|{bot_message.message_id}')]
    ])
    await state.set_state(FiniteStates.default)
    await bot.edit_message_reply_markup(chat_id=chat_id, message_id=bot_message.message_id, reply_markup=markup)


