from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import  Column, Integer, String, Boolean, BigInteger
from bd.connections import pgsql_engine

class Base(DeclarativeBase): pass

class Message(Base):
    __tablename__ = 'messages'

    message_id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(BigInteger, primary_key=True)
    from_user = Column(Integer, index=True)
    from_chat = Column(BigInteger)
    origin_id = Column(Integer)
    type = Column(String)
    answer_id = Column(String)

class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, index=True)
    banned = Column(Boolean)
    subscription = Column(Boolean)
    super_user = Column(Boolean)

Base.metadata.create_all(bind=pgsql_engine)