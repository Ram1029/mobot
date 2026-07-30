import sqlalchemy
from sqlalchemy.orm import sessionmaker
from aiogram.fsm.storage.redis import RedisStorage
from os import getenv

_redis_user, _redis_password = getenv('REDIS_USER'), getenv('REDIS_PASSWORD')
redis_storage = RedisStorage.from_url(f'redix://localhost:6379/telegram-fsm')
#redis_storage = RedisStorage.from_url(f'redix://{_redis_user}:{_redis_password}@localhost:8080/telegram-fsm')

_pgsql_user, _pgsql_password = getenv('PGSQL_USER'), getenv('PGSQL_PASSWORD')
pgsql_engine = sqlalchemy.create_engine(f'postgresql://{_pgsql_user}:{_pgsql_password}@localhost:5432/telegram-entities')

import bd.models
from bd.storage import MessageStorage

pgsql_session = sessionmaker(bind=pgsql_engine, autoflush=False)

global_message_storage = MessageStorage(pgsql_session)