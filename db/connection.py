import os
from ydb.aio import Driver, QuerySessionPool
from ydb.iam import ServiceAccountCredentials
import ydb

YDB_ENDPOINT = os.getenv("YDB_ENDPOINT")
YDB_DATABASE = os.getenv("YDB_DATABASE")

async def create_connection():
    # Глобальный пул соединений YDB (создаётся один раз при холодном старте)
    ydb_driver = Driver(
        endpoint=YDB_ENDPOINT,
        database=YDB_DATABASE,
        credentials=ServiceAccountCredentials(),
        root_certificates=ydb.load_ydb_root_certificate()
    )
    await ydb_driver.wait(timeout=5)
    ydb_pool = QuerySessionPool(ydb_driver, size=5)
    return ydb_driver, ydb_pool

async def indev_connection():
    print("Подключаюсь к базе данных...")
    ydb_driver = Driver(
        endpoint=YDB_ENDPOINT,
        database=YDB_DATABASE,
        credentials=ydb.iam.ServiceAccountCredentials.from_file("db/sa-function.json"),
        root_certificates=ydb.load_ydb_root_certificate(),
    )
    await ydb_driver.wait(timeout=10)
    print("Подключены!")
    ydb_pool = QuerySessionPool(ydb_driver, size=5)
    return ydb_driver, ydb_pool