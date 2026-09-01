from dataclasses import dataclass
from sqlalchemy.orm import Session
from abc import ABC, abstractmethod
from typing import Literal

from bd.models import Message, User

class EntityRecord(ABC):
    """Абстрактный класс записи сущности"""
    @abstractmethod
    def get_object():
        """Возвращает объект модели"""
        pass

    @abstractmethod
    def get_primary_key(self):
        """Возвращает значение первичного ключа"""
        pass


@dataclass
class MessageRecord(EntityRecord):
    message_id: int
    chat_id: int
    from_user: int
    origin_id: int
    type: Literal['posting', 'moderating', 'enquiring', 'question', 'answer', 'answering']
    from_chat: int | None = None
    answer_id: int | None = None
    def __post_init__(self):
        if not self.from_chat:
            self.from_chat = self.from_user

    def get_object(self):
        """Возвращает объект модели"""
        return Message(
            message_id=self.message_id,
            chat_id=self.chat_id,
            from_user=self.from_user,
            from_chat=self.from_chat,
            origin_id=self.origin_id,
            type=self.type,
            answer_id = self.answer_id
        )

    def get_primary_key(self):
        """Возвращает значение первичного ключа"""
        return (self.message_id, self.chat_id)

@dataclass
class UserRecord(EntityRecord):
    user_id: int
    banned: bool = False
    subscription: bool = False
    super_user: bool = False
    def get_object(self):
        return User(
            user_id = self.user_id,
            banned = self.banned,
            subscription = self.subscription,
            super_user = self.super_user
        )
    def get_primary_key(self):
        return self.user_id

class EntityStorage(ABC):
    def __init__(self, session: Session):
        self._session = session
        self._keys = set()
        self._items = {}

    @abstractmethod
    def _model_class(self):
        pass
    @abstractmethod
    def get(self, key):
        pass
    @abstractmethod
    def delete(self, key):
        pass

    def _get_object(self, key):
        obj = self._session.get(self._model_class(), key)
        return obj

    def pop(self, key):
        if key in self._keys:
            self._keys.discard(key)
            instance = self._items.pop(key)
            self._session.delete(instance)
            self.commit()
        else:
            self.delete(key)

    def set(self, record: EntityRecord):
        obj = record.get_object()
        self._session.add(obj)
        self._items[record.get_primary_key()] = obj
        self._session.commit()

    def flush(self):
        self._session.commit()

class MessageStorage(EntityStorage):
    def _model_class(self):
        return Message

    def pop(self, message_id, chat_id):
        key = (message_id, chat_id)
        if key in self._keys:
            self._keys.discard(key)
            instance = self._items.pop(key)
            self._session.delete(instance)
            self.commit()
        else:
            self.delete(message_id, chat_id)
    
    def get(self, message_id, chat_id):
        obj = self._get_object((message_id, chat_id))
        if obj:
            return MessageRecord(
                message_id=obj.message_id,
                chat_id=obj.chat_id,
                from_user=obj.from_user,
                from_chat=obj.from_chat,
                origin_id=obj.origin_id,
                type=obj.type,
                answer_id=int(obj.answer_id) if obj.answer_id else None
            )
        
    def clean(self, user_id: int|str):
        messages = self._session.query(Message).filter(Message.from_user == int(user_id)).all()
        self._session.query(Message).filter(Message.from_user == int(user_id)).delete()
        self._session.commit()
        return messages

    def close_qna(self, message_id: int|str, main_chat_id: int):
        answer_id = self.get(message_id, main_chat_id).answer_id
        question = self.get(message_id=answer_id, chat_id=main_chat_id)
        messages = self._session.query(Message).filter(Message.answer_id==answer_id, Message.chat_id==main_chat_id).all()
        self._session.query(Message).filter(Message.answer_id == answer_id).delete()
        self._session.commit()
        return question, messages

    def close_all_qna(self, main_chat_id):
        messages = self._session.query(Message).filter(Message.answer_id != None, Message.chat_id == main_chat_id).all()
        topics = set()
        for msg in messages:
            topics.add(msg.answer_id)
        questions = []
        for topic in topics:
            questions.append(self.get(topic, main_chat_id))
        self._session.query(Message).filter(Message.answer_id != None).delete()
        self._session.commit()
        return questions, messages
        
    def delete(self, message_id, chat_id):
        instance = self._session.get(Message, (message_id, chat_id))
        if instance:
            self._session.delete(instance)
            self._session.commit()


class UserStorage(EntityStorage):
    def _model_class(self):
        return User
    def get(self, key: str | int):
        obj = self._get_object(key)
        if obj:
            return UserRecord(
                user_id= obj.user_id,
                banned=obj.banned,
                subscription=obj.subscription,
                super_user=obj.super_user
            )
        else:
            answer= UserRecord(user_id=int(key))
            self.set(answer)
            return answer

    def delete(self, key: int | str):
        instance = self._session.query(User).filter(User.user_id == int(key)).first()
        if instance:
            self._session.delete(instance)
            self._session.commit()
        
    def __contains__(self, key: int|str):
        obj = self._get_object(key)
        return bool(obj)
    
    def _set_value(self, key: str, user_id: str|int, value: bool = True):
        user: User = self._get_object(user_id)
        if not user:
            user = UserRecord(int(user_id))
        setattr(user, key, value)
        self._session.add(user)
        self._session.commit()

    def ban(self, user_id: str|int, value: bool = True): self._set_value('banned', user_id, value)
    def subscribe(self, user_id: str|int, value: bool = True): self._set_value('subscription', user_id, value)
    def super_user(self, user_id: str|int, value: bool = True): self._set_value('super_user', user_id, value)

    def get_subscribers(self):
        users = self._session.query(User).filter(User.subscription == True).all()
        return [int(user.user_id) for user in users]