from typing import Literal
from abc import ABC, abstractmethod
import json

class Context(ABC):
    @abstractmethod
    def __init__(self):
        self.context: dict
    def __getitem__(self, key):
        return self.context[key]
    def __setitem__(self): pass
    def __contains__(self, item):
        return item in self.context.keys()
    def get(self, key, default):
        return self.context.get(key, default)

class ChatContext(Context):
    def __init__(self, chat_object: dict):
        self.context = chat_object
        self.type: Literal['private', 'group', 'supergroup', 'channel'] = chat_object['type']
        self.id: int = chat_object['id']
    def isPrivate(self):
        return self.type == 'private'
    def isDirect(self):
        if 'is_direct_message' in self.context.keys():
            return True
        return False
    def isForum(self):
        if 'is_forum' in self.context.keys():
            return True
        return False
    
class MessageContext(Context):
    def __init__(self, message_object: dict):
        self.context = message_object
        self.id: int = message_object['message_id']
        self.chat = ChatContext(message_object['chat'])
        if 'text' in message_object:
            self.text: str = message_object['text']
        else: self.text = ''

class telegramType(ABC):
    @abstractmethod
    def __init__(self, **kwargs):
        self.object = kwargs
    def __str__(self):
        return json.dumps(self.object, default=serialize)

def serialize(object: telegramType | ChatContext):
    match object:
        case telegramType(): return object.object
        case ChatContext(): return object.id

class KeyboardButton(telegramType):
    STYLES = Literal['danger', 'success', 'primary']
    def __init__(self, text: str, style: STYLES = 'primary', icon_custom_emoji_id: str = None):
        self.object = {"text": text}
        if style:
            self.object['style'] = style
        if icon_custom_emoji_id:
            self.object['icon_custom_emoji_id'] = icon_custom_emoji_id

class InlineKeyboardButton(KeyboardButton):
    def __init__(self, text: str, style: str = None, icon_custom_emoji_id: str = None, callback_data: str = None):
        super().__init__(text, style=style, icon_custom_emoji_id=icon_custom_emoji_id)
        if callback_data:
            self.object['callback_data'] = callback_data

class KeyboardMarkup(telegramType): pass

class ReplyKeyboardMarkup(KeyboardMarkup):
    def __init__(self, *buttons):
        self.object = {"keyboard": [*buttons]}

class InlineKeyboardMarkup(KeyboardMarkup):
    def __init__(self, *buttons):
        self.object = {"inline_keyboard": [*buttons]}