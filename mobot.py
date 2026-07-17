import process
from requests import request
from typing import Literal
from motypes import *
import time

class RequestException(Exception):
    def __init__(self, status_code: int, *args):
        super().__init__(*args)
        self.code = status_code
    def __str__(self):
        return f'Request Error, code: {self.code}'
class BadRequest(RequestException):
    def __init__(self, endpoint, method, json,status_code, *args):
        super().__init__(status_code, *args)
        self.msg = f'-> {endpoint}({method}) -> {json}'
    def __str__(self):
        return f'Request Error, code: {self.code}\n{self.msg}'
class Bot():
    API = 'https://api.telegram.org/bot'

    def __init__(self, token: str):
        with open(token, 'r',encoding='UTF-8') as f:
            self.token = f.read()
        self.me = self.method('getMe')
        self.lastUpdate = 0

        self.commands = {}
        self.messageHandler = None

        self.__run = False
        print(f"I'm alive!! It's {self.me['username']}")

    def method(self, endpoint: str, method: Literal['GET', 'POST'] = 'GET', **kwargs):
        url = f'{self.API}{self.token}/{endpoint}'
        if len(kwargs) < 1:
            print(url)
            responce = request(method, url)
        else:
            jsondata = json.dumps(kwargs, default=serialize, ensure_ascii=False)
            responce = request(method, url, data=jsondata, headers={'Content-Type':'application/json'})
        if responce.status_code == 200:
            answer = responce.json()
            if answer['ok']:
                return answer.get('result', [])
        elif responce.status_code == 429:
            time.sleep(0.2)
        elif responce.status_code == 400:
            raise BadRequest(endpoint, method, jsondata, responce.status_code)
        raise RequestException(responce.status_code)

        return False
    
    @property
    def run(self): return self.__run

    @run.setter
    def run(self, value: bool):
        self.__run = value
        while self.__run:
            try:
                self.update()
                time.sleep(1/20)
            except KeyboardInterrupt:
                self.__run = False
                print('Завершаю работу...')
            except BadRequest as e:
                self.__run = False
                print("Плохой запрос!", e)
            except RequestException as e:
                print(e)
            #except BaseException as e:
            #    print(f'!!!Exception {type(e)}:', e)

    def get_updates(self):
        updates = self.method('getUpdates', offset=self.lastUpdate+1)
        if not updates:
            return self.get_updates()
        updates.sort(key= lambda x: x['update_id'])
        return updates
    
    def update(self):
        updates = self.get_updates()
        for update in updates:
            process.process(self, update)
        self.lastUpdate = updates[-1]['update_id']
    
    def sendMessage(self, text, chatId: int, **kwargs):
        self.method('sendMessage', text = text, chat_id=chatId, **kwargs)

    def copyMessage(self, chat_id: int, message_id: int, from_chat_id: int = None, reply_markup: KeyboardMarkup = None, **kwargs):
        if not from_chat_id:
            from_chat_id = chat_id
        if not reply_markup:
            self.method('copyMessage', chat_id=chat_id, from_chat_id=from_chat_id, message_id=message_id, **kwargs)
        else:
            self.method('copyMessage', chat_id=chat_id, from_chat_id=from_chat_id, message_id=message_id, reply_markup=reply_markup, **kwargs)

    def addCommand(self, cmd: str):
        def decor(func):
            self.commands[cmd] = func
            return func
        return decor

    def callCommand(self, cmd: str, context: MessageContext):
        if cmd in self.commands.keys():
            handler = self.commands[cmd]
            handler(context)

    def message(self, func):
        self.messageHandler = func