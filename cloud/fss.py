from typing import Optional

from ydb.aio import QuerySessionPool
from cloud.storages import CloudStorage
from aiogram.fsm.storage.base import BaseStorage
from datetime import datetime, timezone, timedelta

from cloud.records import SessionRecord

class FiniteStatesStorage(CloudStorage, BaseStorage):
    def __init__(self, pool: QuerySessionPool):
        super().__init__()
        self._pool = pool

    async def _load_from_db(self, key: str) -> Optional[SessionRecord]:
        user_id, bot_id = map(int, key.split(':'))
        result = await self._pool.execute_with_retries(
            "SELECT * FROM sessions WHERE user_id = $uid0 AND bot_id = $uid1",
            parameters={"$uid0": user_id, "$uid1": bot_id}
        )
        rows = result[0].rows
        if not rows:
            return None
        row = rows[0]
        return SessionRecord(
            user_id=row.user_id,
            bot_id=row.bot_id,
            state_id=row.state_id or 0,
            last_update=row.last_update
        )

    async def set_state(self, key, state = None):
        if state:
            state = SessionRecord.index_state(state)
        else:
            state = 0
        new_record = SessionRecord(user_id=key.user_id, bot_id=key.bot_id, state_id=state, last_update=datetime.now(timezone.utc))
        self.set(record=new_record)

    async def get_state(self, key):
        record_key = f'{key.user_id}:{key.bot_id}'
        record: SessionRecord = await self.get(record_key)
        if record:
            last_update = record.last_update.replace(tzinfo=timezone.utc)
            delta = datetime.now(timezone.utc) - last_update
            state = SessionRecord.from_index(record.state_id)
            if delta < timedelta(minutes=10):
                return state
            self.delete(record)
        new_record = SessionRecord(user_id=key.user_id, bot_id=key.bot_id, state_id=0, last_update=datetime.now(timezone.utc))
        self.set(record=new_record)
        return 0

    async def set_data(self, key, data): pass
    async def get_data(self, key): pass
    async def close(self):
        await self.flush(self._pool)