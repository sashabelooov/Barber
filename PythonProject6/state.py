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
    select_date = State()
    select_time = State()
    conf_booking = State()
    sana = State()
    conf_book_and_payment = State()
    payment = State()
    check_payment = State()
    service_type = State()