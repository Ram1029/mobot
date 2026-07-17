from mobot import Bot
from motypes import *
import json
from botdata import *
import time

f = open("strings.json", encoding='UTF-8')
strings = json.load(f)
f.close()
memory = Memory()


mochem = Bot("token")

@mochem.addCommand('start')
def start(context: MessageContext):
    if context.chat.isPrivate():
        msg = strings['helloMessage']
        markup = ReplyKeyboardMarkup(
            [KeyboardButton(strings['sendMessage'],icon_custom_emoji_id='5282857993677860851')]
        )
        mochem.sendMessage(msg, context.chat, reply_markup = markup)

@mochem.addCommand('echo')
def test(context: MessageContext):
    mochem.sendMessage('Hewo I\'m a living MO chem app! ^-^', context.chat)

@mochem.addCommand('cancel')
def cancel(msg: MessageContext):
    if Record(msg.chat, 'sending') in memory:
        memory.pop(msg.chat.id)
        mochem.sendMessage(strings['cancelMessage'], msg.chat)

@mochem.message
def message(msg: MessageContext):
    sending = Record(msg.chat, 'sending')
    if sending in memory:
        lastActivation = memory.read(sending)['time']
        if time.time() - lastActivation < 300:
            markup = InlineKeyboardMarkup(
                [InlineKeyboardButton('Отправить', callback_data='send')],
                [InlineKeyboardButton('Отменить', callback_data='cancel')]
            )
            mochem.copyMessage(msg.chat, msg.id, reply_markup=markup)
        else:
            memory.pop(sending)
    if msg.chat.isPrivate():
        if msg.text.endswith(strings["sendMessage"]):
            sending.value = {'time': time.time()}
            memory.write(sending)
            mochem.sendMessage(strings['offer'], msg.chat)
        match msg.get('entities', []):
            case [{'offset': 0, 'type':'custom_emoji', 'custom_emoji_id': custom_id}]:
                mochem.sendMessage(f'ID кастомного емодзи: {custom_id}', msg.chat)

mochem.run = True