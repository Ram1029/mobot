from aiogram.fsm.state import StatesGroup, State
from typing import Literal

class FiniteStates(StatesGroup):
    default = State()
    posting = State()
    enquiring = State()

class StoragedMessage():
    message_types = Literal['posting', 'moderating']
    def __init__(self, from_user: int, message_type: message_types, from_chat: int = None, origin: int = None):
        self.from_user = from_user
        self.type = message_type
        if from_chat:
            self.from_chat = from_chat
        else:
            self.from_chat = from_user
        self.origin = origin

class MessageStorage():
    def __init__(self):
        self.__storage = {}
        self.__keys = []
    def pop(self, message_id: int):
        if message_id in self.__keys:
            self.__storage.pop(message_id)
            self.__keys.remove(message_id)
    def __getitem__(self, message_id: int):
        if message_id in self.__keys:
            return self.__storage[message_id]
    def __setitem__(self, message_id: int, message: StoragedMessage):
        if message_id in self.__keys:
            self.__storage[message_id] = message
        else:
            self.__keys.append(message_id)
            self.__storage[message_id] = message
    def __contains__(self, message_id: int):
        return message_id in self.__keys

global_message_storage = MessageStorage()

def get_message_storage():
    global global_message_storage
    return global_message_storage