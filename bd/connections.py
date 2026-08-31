import sqlalchemy
from sqlalchemy.orm import sessionmaker
from aiogram.fsm.storage.redis import RedisStorage
from os import getenv

redis_storage = RedisStorage.from_url(getenv('REDIS_URL', 'redis://localhost:6379/0'))
redis_storage.state_ttl = 600

_pgsql_user = getenv('PGSQL_USER', 'postgres')
_pgsql_password = getenv('PGSQL_PASSWORD', '')
_pgsql_host = getenv('PGSQL_HOST', 'localhost')
_pgsql_port = getenv('PGSQL_PORT', '5432')
_pgsql_db = getenv('PGSQL_DB', 'telegram-entities')
pgsql_engine = sqlalchemy.create_engine(
	f'postgresql://{_pgsql_user}:{_pgsql_password}@{_pgsql_host}:{_pgsql_port}/{_pgsql_db}'
)

import bd.models
from bd.storage import MessageStorage, UserStorage

pgsql_session = sessionmaker(bind=pgsql_engine, autoflush=False)()

global_message_storage = MessageStorage(pgsql_session)
global_user_storage = UserStorage(pgsql_session)