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


@dataclass
class MessageRecord(EntityRecord):
    message_id: int
    from_user: int
    origin_id: int
    type: Literal['posting', 'moderating', 'enquiring', 'question', 'answer']
    from_chat: int | None = None
    answer_id: int | None = None
    def __post_init__(self):
        if not self.from_chat:
            self.from_chat = self.from_user

    def get_object():
        pass

class EntityStorage(ABC):
    def __init__(self, session: Session):
        self._session = session
        self._keys = set()
        self._items = {}

    @abstractmethod
    def _model_class(self):
        pass

    def get(self, key: int | str):
        key = int(key)
        self._session.get(self._model_class, key)

    def pop(self, key: int | str):
        key = int(key)
        if key in self._keys:
            self._keys.discard(key)
            self._items.pop(key)

    def set(self, record: EntityRecord):
        obj = record.get_object()
        self._session.set(obj)

    def flush(self):
        self._session.commit()

class MessageStorage(EntityStorage):
    def _model_class(self):
        return Message