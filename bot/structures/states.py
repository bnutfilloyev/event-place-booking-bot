from aiogram.filters.state import State, StatesGroup


class RegState(StatesGroup):
    fullname = State()
    phone_number = State()

    guest_fullname = State()
    guest_phone_number = State()
    guest_badge_number = State()
    


class BroadcastState(StatesGroup):
    broadcast = State()
