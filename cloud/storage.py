from ydb.aio import QuerySessionPool
import ydb
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional
from typing import Any
from datetime import datetime

from cloud.records import CloudRecord, Operation

T = TypeVar("T", bound=CloudRecord)


class CloudStorage(ABC, Generic[T]):
    """
    Абстрактное in-memory хранилище с отложенной записью в YDB.

    - Хранит записи в dict по первичному ключу
    - Отслеживает dirty-записи
    - Умеет формировать batch YQL-запрос
    """

    def __init__(self):
        self._cache: dict[str, T] = {}       # key → record
        self._dirty: dict[str, T] = {}       # key → dirty record
        self._notexists: list[str] = []       # key -> notexist

    # ── Чтение ──────────────────────────────────────────────

    @abstractmethod
    async def _load_from_db(self, key: str) -> Optional[T]:
        """Загрузить запись из YDB по ключу (кэш-промах)."""
        ...

    def _make_key(self, record: CloudRecord) -> str:
        """Строковый ключ для dict-кэша."""
        pk = record.get_primary_key()
        return ":".join(str(v) for v in pk.values())

    async def get(self, key: str) -> Optional[T]:
        """Достать запись: из кэша или из YDB."""
        # 0. Смотрим, знаем ли мы о ней что-то (может такого существа нету вообще?)
        if key in self._notexists:
            return None

        # 1. Сначала смотрим dirty (там самые свежие данные)
        if key in self._dirty:
            return self._dirty[key]

        # 2. Потом в чистом кэше
        if key in self._cache:
            return self._cache[key]

        # 3. Кэш-промах — грузим из YDB
        record = await self._load_from_db(key)
        if record:
            self._cache[key] = record
        else:
            self._notexists.append(key)
        return record

    # ── Запись ──────────────────────────────────────────────

    def set(self, record: T) -> None:
        """Сохранить запись в кэше (пометит как dirty)."""
        key = self._make_key(record)
        record.mark_upsert()
        if key in self._notexists:
            self._notexists.remove(key)
        self._dirty[key] = record

    def delete(self, record: T) -> None:
        """Пометить запись на удаление."""
        key = self._make_key(record)
        record.mark_deleted()
        self._dirty[key] = record
        self._notexists.append(key)

    # ── Формирование batch-запроса ──────────────────────────
    @staticmethod
    def _to_typed_value(val) -> ydb.TypedValue:
        """Оборачивает Python-значение в ydb.TypedValue с явным типом."""
        if isinstance(val, bool):
            return ydb.TypedValue(int(val), ydb.PrimitiveType.Uint64)
        if isinstance(val, int):
            return ydb.TypedValue(val, ydb.PrimitiveType.Int64)
        if isinstance(val, float):
            return ydb.TypedValue(val, ydb.PrimitiveType.Double)
        if isinstance(val, str):
            return ydb.TypedValue(val, ydb.PrimitiveType.Utf8)
        if isinstance(val, bytes):
            return ydb.TypedValue(val, ydb.PrimitiveType.String)
        if isinstance(val, datetime):
            return ydb.TypedValue(val, ydb.PrimitiveType.Timestamp)
        if val is None:
            return ydb.TypedValue("", ydb.PrimitiveType.Utf8)  # fallback
        return ydb.TypedValue(str(val), ydb.PrimitiveType.Utf8)  # fallback


    @staticmethod
    def _ydb_type_name(val) -> str:
        """Имя YDB-типа для DECLARE."""
        if isinstance(val, bool):
            return "Uint64"
        if isinstance(val, int):
            return "Int64"
        if isinstance(val, float):
            return "Double"
        if isinstance(val, str):
            return "Utf8"
        if isinstance(val, bytes):
            return "String"
        if isinstance(val, datetime):
            return "Timestamp"
        return "Utf8"

    def build_flush_query(self) -> tuple[str, dict[str, Any]]:
        """
        Собирает один YQL-запрос из всех dirty-записей.

        Возвращает (yql_text, parameters).
        """
        if not self._dirty:
            return "", {}

        statements: list[str] = []
        declares: list[str] = []
        params: dict[str, ydb.TypedValue] = {}
        idx = 0

        for key, record in self._dirty.items():
            if record.operation == Operation.DELETE:
                pk = record.get_primary_key()
                conditions = " AND ".join(
                    f"`{col}` = ${col}{idx}" for col in pk
                )
                statements.append(
                    f"DELETE FROM `{record.get_table_name()}` WHERE {conditions}"
                )
                for col, val in pk.items():
                    params[f"${col}{idx}"] = self._to_typed_value(val)
                    declares.append(f"DECLARE ${col}{idx} AS {self._ydb_type_name(val)};")
                idx += 1

            elif record.operation == Operation.UPSERT:
                all_fields = record.get_all_fields()
                cols = ", ".join(f"`{k}`" for k in all_fields)
                vals = ", ".join(f"${k}{idx}" for k in all_fields)
                statements.append(
                    f"UPSERT INTO `{record.get_table_name()}` ({cols}) VALUES ({vals})"
                )
                for col, val in all_fields.items():
                    params[f"${col}{idx}"] = self._to_typed_value(val)
                    declares.append(f"DECLARE ${col}{idx} AS {self._ydb_type_name(val)};")
                idx += 1

        unique_declares = list(dict.fromkeys(declares))
        yql = "\n".join(unique_declares) + "\n" + ";\n".join(statements) + ";"
        return yql, params

    # ── Сброс dirty после записи ────────────────────────────

    def mark_clean(self) -> None:
        """Перенести dirty → cache (после успешного flush в YDB)."""
        for key, record in self._dirty.items():
            if record.operation == Operation.DELETE:
                self._cache.pop(key, None)
            else:
                self._cache[key] = record
        self._dirty.clear()

    async def flush(self, pool) -> None:
        """
        Записывает все dirty-изменения в YDB одним запросом.
        Вызывать в конце каждого handler'а.
        """
        if not self._dirty:
            return

        yql, params = self.build_flush_query()
        if not yql:
            return

        await pool.execute_with_retries(yql, parameters=params)
        self.mark_clean()

