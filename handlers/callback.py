from aiogram import Bot, Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from os import getenv

from bd.storage import MessageRecord
from bd.connections import global_message_storage, global_user_storage

from mobot.phrases import phrases
import mobot.keyboards as kb

router = Router()

message_storage = global_message_storage
user_storage = global_user_storage

main_channel_id = getenv('MAIN_CHANNEL_ID')
main_chat_id = int(getenv('MAIN_CHAT_ID'))
suggestions_topic_id = int(getenv('SUGGESTIONS_TOPIC_ID'))
questions_topic_id = int(getenv('QUESTIONS_TOPIC_ID'))

@router.callback_query()
async def callback_handler(callback: CallbackQuery, bot: Bot, state: FSMContext):
    data = callback.data.split('|')
    text = None

    substract = str(data[1])
    match data[0]:
        case 'subscribe':
            state_data = await state.get_data()
            if start_message_id not in state_data:
                return
            text = phrases.subscribe_callback_text
            start_message_id = state_data['start_message_id']
            inline_markup = kb.start_inline_keyboard_without_subscribtion
            await bot.edit_message_reply_markup(message_id=start_message_id, chat_id=callback.from_user.id, reply_markup=inline_markup)
            user_id = callback.from_user
            user_storage.subscribe(user_id)
            await bot.send_message(chat_id=user_id,text=phrases.subscribe_text,reply_markup=kb.reply_keyboard_without_subscribtion,reply_to_message_id=start_message_id)

        case 'cancel':
            text = phrases.cancel_text
            await bot.edit_message_reply_markup(message_id=substract, chat_id=callback.from_user.id)
            message_storage.pop(substract)

        case 'send':
            text = phrases.send_text
            posting_message: MessageRecord = message_storage.get(substract)
            if not posting_message:
                await bot.answer_callback_query(callback.id, text='missing data')
                return
            bot_message = await bot.copy_message(from_chat_id=posting_message.from_chat, message_id=posting_message.origin_id, chat_id=main_chat_id, message_thread_id=suggestions_topic_id)
            message_storage.pop(substract)
            message_storage.set(MessageRecord(message_id=bot_message.message_id,from_user=callback.from_user.id, type='moderating', origin_id=posting_message.origin_id))
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=phrases.send, callback_data=f'post|{bot_message.message_id}')],
                [InlineKeyboardButton(text=phrases.cancel, callback_data=f'decline|{bot_message.message_id}')]
            ])
            await bot.edit_message_reply_markup(message_id=substract, chat_id=callback.from_user.id)
            await bot.edit_message_reply_markup(chat_id=main_chat_id, message_id=bot_message.message_id, reply_markup=markup)

        case 'post':
            text = phrases.post_text
            moderating_message: MessageRecord = message_storage.get(substract)
            if not moderating_message:
                await bot.answer_callback_query(callback.id, text='missing data')
                return
            await bot.copy_message(chat_id=main_channel_id, from_chat_id=moderating_message.from_user, message_id=moderating_message.origin_id)
            await bot.delete_message(chat_id=main_chat_id, message_id=substract)
            message_storage.pop(substract)

        case 'decline':
            text = phrases.decline_text
            await bot.delete_message(chat_id=main_chat_id, message_id=substract)
            message_storage.pop(substract)

        case 'ask':
            text = phrases.ask_text
            enquiring_message: MessageRecord = message_storage.get(substract)
            if not enquiring_message:
                await bot.answer_callback_query(callback.id, text='missing data')
                return
            bot_message = await bot.copy_message(from_chat_id=enquiring_message.from_chat, message_id=enquiring_message.origin_id, chat_id=main_chat_id, message_thread_id=questions_topic_id)
            message_storage.pop(substract)
            message_storage.set(MessageRecord(message_id=bot_message.message_id,from_user=callback.from_user.id, type='question', origin_id=posting_message.origin_id))
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=phrases.close, callback_data=f'close|{bot_message.message_id}')]
            ])
            await bot.edit_message_reply_markup(message_id=substract, chat_id=callback.from_user.id)
            await bot.edit_message_reply_markup(chat_id=main_chat_id, message_id=bot_message.message_id, reply_markup=markup)

        case 'close':
            question_message = message_storage.get(substract)
            if not question_message.answer_id:
                text = phrases.close_text
                message_storage.pop(question_message)
                await bot.send_message(chat_id=question_message.from_user, text=phrases.closed, reply_to_message_id=question_message.origin_id)
                await bot.delete_message(message_id=question_message.message_id, chat_id=main_chat_id)
            else:
                await bot.edit_message_reply_markup(chat_id=main_chat_id, message_id=substract)

    await bot.answer_callback_query(callback.id, text=text)
