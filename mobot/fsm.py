from aiogram.fsm.state import StatesGroup, State
from typing import Literal

class MessageStates(StatesGroup):
    posting = State()
    enquiring = State()
    supering = State()