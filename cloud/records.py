from ydb.aio import QuerySessionPool
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from time import time
from datetime import datetime, timezone

from aiogram.fsm.state import State
from mobot.fsm import FiniteStates

states = [FiniteStates.default, FiniteStates.posting, FiniteStates.enquiring]

class Operation(Enum):
    UPSERT = 'UPSERT'
    DELETE = 'DELETE'

@dataclass
class CloudRecord(ABC):
    """
    Абстрактная запись, которая отслеживает своё состояние.
    """
    _operation: Operation = field(default=Operation.UPSERT, init=False, repr=False)
    _dirty_fields: set[str] = field(default_factory=set, init=False, repr=False)

    @abstractmethod
    def get_table_name(self) -> str:
        """Имя таблицы в YDB."""
        ...

    @abstractmethod
    def get_primary_key(self) -> dict[str, Any]:
        """Поля первичного ключа: {'user_id': 123}."""
        ...

    @abstractmethod
    def get_all_fields(self) -> dict[str, Any]:
        """Все поля записи для UPSERT."""
        ...

    def mark_dirty(self, field_name: str) -> None:
        """Отметить поле как изменённое."""
        self._dirty_fields.add(field_name)

    def mark_deleted(self) -> None:
        """Пометить запись на удаление."""
        self._operation = Operation.DELETE

    def mark_upsert(self) -> None:
        """Пометить запись на вставку/обновление."""
        self._operation = Operation.UPSERT

    @property
    def is_dirty(self) -> bool:
        return bool(self._dirty_fields) or self._operation == Operation.DELETE

    @property
    def operation(self) -> Operation:
        return self._operation

@dataclass
class SessionRecord(CloudRecord):
    """Запись финального состояния сессии пользователя"""
    user_id: int
    bot_id: int
    state_id: int = 0
    last_update: datetime | None = None

    def from_index(index: int):
        global states
        if index < len(states):
            return states[index]
        else:
            raise IndexError()

    def index_state(state: State):
        global states
        if state in states:
            return states.index(state)
        else:
            raise KeyError()

    def get_table_name(self) -> str:
        return 'sessions'
    
    def get_primary_key(self) -> dict[int, Any]:
        return {
            "user_id": self.user_id,
            "bot_id": self.bot_id
        }
    
    def get_all_fields(self) -> dict[str, Any]:

        returning = {
            "user_id": self.user_id,
            "bot_id": self.bot_id,
            "state_id": self.state_id,
            "last_update": self.last_update or datetime.now(timezone.utc)
        }
        print(returning)
        return returning