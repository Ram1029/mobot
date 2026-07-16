from mobot import Bot
from motypes import *
import json
import time

f = open("strings.json", encoding='UTF-8')
strings = json.load(f)
f.close()
memory = {}

mochem = Bot("token")

@mochem.addCommand('start')
def start(context: MessageContext):
    if context.chat.isPrivate():
        msg = strings['helloMessage']
        markup = ReplyKeyboardMarkup(
            [KeyboardButton(strings['sendMessage'])]
        )
        mochem.sendMessage(msg, context.chat, reply_markup = markup)

@mochem.addCommand('echo')
def test(context: MessageContext):
    mochem.sendMessage('Hewo I\'m a living MO chem app! ^-^', context.chat)

@mochem.addCommand('cancel')
def cancel(msg: MessageContext):
    if msg.chat.id in memory.keys():
        memory.pop(msg.chat.id)
        mochem.sendMessage(strings['cancelMessage'], msg.chat)

@mochem.message
def message(msg: MessageContext):
    if msg.chat.id in memory.keys():
        lastActivation = memory[msg.chat.id]
        if time.time() - lastActivation < 300:
            mochem.method('copyMessage', chat_id=msg.chat, from_chat_id=msg.chat, message_id=msg.id, reply_markup = InlineKeyboardMarkup([InlineKeyboardButton('Отправить', callback_data='send')],[InlineKeyboardButton('Отменить',callback_data='cancel')]))
    if msg.chat.isPrivate():
        if msg.text.endswith(strings["sendMessage"]):
            memory[msg.chat.id] = time.time()
            mochem.sendMessage(strings['offer'], msg.chat)

mochem.run = True