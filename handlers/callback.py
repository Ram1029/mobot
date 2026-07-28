from aiogram import Bot, Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from os import getenv

from mobot.phrases import phrases
from mobot.fsm import FiniteStates, StoragedMessage, get_message_storage

router = Router()

message_storage = get_message_storage()

main_channel_id = getenv('MAIN_CHANNEL_ID')
main_chat_id = int(getenv('MAIN_CHAT_ID'))
suggestions_topic_id = int(getenv('SUGGESTIONS_TOPIC_ID'))

@router.callback_query()
async def callback_handler(callback: CallbackQuery, bot: Bot):
    data = callback.data.split('|')
    text = None
    substract = int(data[1])
    match data[0]:
        case 'cancel':
            text = phrases.cancel_text
            await bot.edit_message_reply_markup(message_id=substract, chat_id=callback.from_user.id)
            message_storage.pop(substract)
        case 'send':
            text = phrases.send_text
            posting_message: StoragedMessage = message_storage[substract]
            bot_message = await bot.copy_message(from_chat_id=posting_message.from_chat, message_id=posting_message.origin, chat_id=main_chat_id, message_thread_id=suggestions_topic_id)
            message_storage.pop(substract)
            message_storage[bot_message.message_id] = StoragedMessage(callback.from_user.id, 'moderating', origin=posting_message.origin)
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=phrases.send, callback_data=f'post|{bot_message.message_id}')],
                [InlineKeyboardButton(text=phrases.cancel, callback_data=f'decline|{bot_message.message_id}')]
            ])
            await bot.edit_message_reply_markup(message_id=substract, chat_id=callback.from_user.id)
            await bot.edit_message_reply_markup(chat_id=main_chat_id, message_id=bot_message.message_id, reply_markup=markup)
        case 'post':
            text = phrases.post_text
            moderating_message: StoragedMessage = message_storage[substract]
            await bot.copy_message(chat_id=main_channel_id, from_chat_id=moderating_message.from_user, message_id=moderating_message.origin)
            await bot.delete_message(chat_id=main_chat_id, message_id=substract)
            message_storage.pop(substract)
        case 'decline':
            text = phrases.decline_text
            await bot.delete_message(chat_id=main_chat_id, message_id=substract)
            message_storage.pop(substract)
    await bot.answer_callback_query(callback.id, text=text)
