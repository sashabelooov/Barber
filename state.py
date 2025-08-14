from aiogram.fsm.state import State, StatesGroup


class UserState(StatesGroup):
    language = State()
    phone = State()
    fio = State()
    conf = State()
    menu = State()
    show_contact_or_location = State()
    change_language = State()
    barber_name = State()
    booking_history = State()
    service_type = State()
    check_service_type = State()
    type_of_selected_service = State()
    select_date = State()
