from aiogram.fsm.state import State, StatesGroup


class ImageForm(StatesGroup):
    image = State()
    command = State()
    shakalize = State()
    waiting_for_text = State()
