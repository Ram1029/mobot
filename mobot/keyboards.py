from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from mobot.phrases import phrases

reply_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [KeyboardButton(text=phrases.post_message, icon_custom_emoji_id='5282857993677860851')],
    [KeyboardButton(text=phrases.make_question, icon_custom_emoji_id='5314321889001241271')],
    [KeyboardButton(text=phrases.subscribe, icon_custom_emoji_id='5316505222741259250')]
])
reply_keyboard_without_subscribtion = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [KeyboardButton(text=phrases.post_message, icon_custom_emoji_id='5282857993677860851')],
    [KeyboardButton(text=phrases.make_question, icon_custom_emoji_id='5314321889001241271')]
])
start_inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=phrases.post_message, icon_custom_emoji_id='5282857993677860851')],
    [InlineKeyboardButton(text=phrases.make_question, icon_custom_emoji_id='5314321889001241271')],
    [InlineKeyboardButton(text=phrases.subscribe_callback, icon_custom_emoji_id='5316505222741259250', callback_data='subscribe')]
])
start_inline_keyboard_without_subscribtion = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=phrases.post_message, icon_custom_emoji_id='5282857993677860851')],
    [InlineKeyboardButton(text=phrases.make_question, icon_custom_emoji_id='5314321889001241271')]
])