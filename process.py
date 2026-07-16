#from main import Bot
from abc import ABC, abstractmethod
from motypes import *

class Bot(ABC):
    @abstractmethod
    def __init__(self):
        self.me, self.messageHandler
    @abstractmethod
    def callCommand(): pass

def message(self: Bot, message: MessageContext):
    text = message.text
    if 'entities' in message:
        for messageEntity in message["entities"]:
            if messageEntity['type'] == "bot_command" and not messageEntity['offset']:
                cmd = text[1:messageEntity['length']]
                if '@' in cmd:
                    splitted = cmd.split('@')
                    cmd = '@'.join(splitted[:-1])
                    if splitted[-1] != self.me['username']:
                        continue
                context = message
                self.callCommand(cmd, context)
                return
    self.messageHandler(message)

PROCESSORS = {
    'message': message
}

def process(self: Bot, update: dict):
    match update:
        case {'message': msg}:
            message(self, MessageContext(msg))