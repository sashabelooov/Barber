import json
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import LabeledPrice
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from decouple import config
from aiogram.enums import ChatAction
from aiogram import F
from aiogram.types import Message, SuccessfulPayment
from aiogram import types
from aiogram.fsm.state import default_state
from aiogram.filters import StateFilter

# local modules
from api import create_user, is_user_exists
from state import UserState
import keyboards as kb


TOKEN = config('TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()


with open("data.json", "r", encoding="utf-8") as file:
    translations = json.load(file)


def get_text(lang, category, key):
    return translations.get(lang, {}).get(category, {}).get(key, f"[{key}]")


user_lang = {"uz":"🇺🇿 uz", "ru":"🇷🇺 ru"}


@router.message(F.text, StateFilter(default_state))
async def start(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        old_state = await state.get_state()

        if old_state:
            return

        await bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
        user_info = await is_user_exists(user_id)
        if user_info:
            lang = user_info["language"]
            lang = user_lang[lang]
            await state.update_data(language=lang)
            await message.answer(text=get_text(lang, 'message_text', 'menu'), reply_markup=kb.menu(lang))
            await state.set_state(UserState.menu)
        else:
            await bot.send_message(
                chat_id=user_id,
                text=translations['start'],
                reply_markup=kb.start_key(),
                parse_mode='HTML'
            )
            await state.set_state(UserState.language)

    except Exception as error:
        print(error)




@router.message(UserState.language)
async def ask_phone(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text in {"🇺🇸 eng":"🇺🇸 eng","🇺🇿 uz":"🇺🇿 uz","🇷🇺 ru":"🇷🇺 ru",}:
        await state.update_data(language=message.text)
        data = await state.get_data()
        lang = data['language']
        await bot.send_message(chat_id=user_id,text=get_text(lang, 'message_text', 'phone'), reply_markup=kb.ask_phone(lang))
        await state.set_state(UserState.phone)



@router.message(UserState.phone)
async def check_phone(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    lang = data['language']
    if message.contact:
        await state.update_data(phone=message.contact.phone_number)
        await bot.send_message(chat_id=user_id,text=get_text(lang, 'message_text', 'name'), reply_markup=ReplyKeyboardRemove())
        await state.set_state(UserState.fio)
    else:
        text = message.text
        if message.text.startswith("+998") and len(text) == 13 and text[1:].isdigit():
            await state.update_data(phone=message.text)
            await bot.send_message(chat_id=user_id,text=get_text(lang, 'message_text', 'name'), reply_markup=ReplyKeyboardRemove())
            await state.set_state(UserState.fio)
        else:
            await bot.send_message(chat_id=user_id,text=get_text(lang, 'message_text', 'error_phone'))



@router.message(UserState.fio)
async def fio_user(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    lang = data['language']
    ok = True
    for i in message.text:
        if not i.isalpha():
            await bot.send_message(chat_id=user_id,text=get_text(lang, 'message_text', 'error_name'))
            ok = False
            break
    if ok:
        await state.update_data(user_name=message.text)
        msg_text = (
            f"{get_text(lang, 'message_text', 'confirmed_userinfo')}\n"
            f"{get_text(lang, 'message_text', 'conf_phone')} {data["phone"]}\n"
            f"{get_text(lang, 'message_text', 'conf_name')} {message.text}\n"
        )

        await bot.send_message(chat_id=user_id,text=msg_text, reply_markup=kb.conf(lang))
        await state.set_state(UserState.conf)



@router.message(UserState.conf)
async def check_conf_customer(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        data = await state.get_data()
        lang = data['language']

        if message.text == get_text(lang, "buttons", "confirm"):
            if await create_user(user_id, data['phone'] ,data['user_name'], lang):
                await message.answer(text=get_text(lang, 'message_text', 'menu'), reply_markup=kb.menu(lang))
                await state.set_state(UserState.menu)

        if message.text == get_text(lang, "buttons", "rejected"):
            await bot.send_message(
                chat_id=user_id,
                text=translations['start'],
                reply_markup=kb.start_key(),
                parse_mode='HTML'
            )
            await state.set_state(UserState.language)

    except Exception as e:
        print(f"Error:{e}")




@router.message(UserState.menu)
async def menu_check_button(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        data = await state.get_data()
        lang = data['language']

        if message.text == get_text(lang, "buttons", "contact_menu"):
            await message.answer(text=get_text(lang, 'message_text', 'show_contact'),
                                 reply_markup=kb.back(lang))
            await state.set_state(UserState.show_contact_or_location)

        if message.text == get_text(lang, "buttons", "location"):
            await bot.send_location(chat_id=user_id, latitude=41.330286, longitude=69.345200)
            await message.answer(text=get_text(lang, 'message_text', 'show_location'),
                                 reply_markup=kb.back(lang))
            await state.set_state(UserState.show_contact_or_location)

        if message.text == get_text(lang, "buttons", "change_lang"):
            await message.answer(text=get_text(lang, 'message_text', 'change_language'),
                                 reply_markup=kb.language(lang))
            await state.set_state(UserState.change_language)

        #////////// Booking History databaseda obchiqish kerey \\\\\\\\\\\# hozricha booking hisotry yoq dib yozib turaman
        if message.text == get_text(lang, "buttons", "booking_history"):
            await message.answer(text=get_text(lang, 'message_text', 'no_booking_history'),
                                 reply_markup=kb.back(lang))
            await state.set_state(UserState.show_contact_or_location)

        # ////////// Booking databaseda Isimlani obchiqish kerey \\\\\\\\\\\ #
        if message.text == get_text(lang, "buttons", "booking"):
            await message.answer(text=get_text(lang, 'message_text', 'service_type'),
                                 reply_markup=kb.service_type(lang))
            await state.set_state(UserState.service_type)
            # await message.answer(text=get_text(lang, 'message_text', 'barber_name'), reply_markup= await kb.barber_name(lang))
            # await state.set_state(UserState.barber_name)

    except Exception as e:
        print(f"Error:{e}")




@router.message(UserState.show_contact_or_location)
async def show_contact_or_location(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        data = await state.get_data()
        lang = data['language']
        if message.text == get_text(lang, "buttons", "back"):
            await message.answer(text=get_text(lang, 'message_text', 'menu'), reply_markup=kb.menu(lang))
            await state.set_state(UserState.menu)

    except Exception as e:
        print(f"Error:{e}")




@router.message(UserState.change_language)
async def change_language(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        data = await state.get_data()
        lang = data['language']

        if message.text == get_text(lang, "buttons", "back"):
            await message.answer(text=get_text(lang, 'message_text', 'menu'), reply_markup=kb.menu(lang))
            await state.set_state(UserState.menu)
            return

        # ///////// TILNI SHU JOYDA O'ZGARTIRILADI \\\\\\\\\\\\\ #   databaseda ham update qilish kerey
        selected_language = message.text.split(" ")[1]
        await state.update_data(language=message.text)  # 🌟 YANGILADI!
        await message.answer(text=get_text(message.text, 'message_text', 'menu'), reply_markup=kb.menu(message.text))
        await state.set_state(UserState.menu)

    except Exception as e:
        print(f"Error: {e}")






@router.message(UserState.service_type)
async def service_type(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        data = await state.get_data()
        lang = data['language']

        if message.text == get_text(lang, "buttons", "back"):
            await message.answer(text=get_text(lang, 'message_text', 'menu'), reply_markup=kb.menu(lang))
            await state.set_state(UserState.menu)

        if message.text == get_text(lang, "buttons", "hair") or message.text == get_text(lang, "buttons", "hair_beard"):
            await state.update_data(service_type=message.text)
            inline_keyboard, simple_keyboard = await kb.barber_name(lang)
            await message.answer(text=get_text(lang, 'message_text', 'barber_name_2'), reply_markup=simple_keyboard)
            await message.answer(text=get_text(lang, 'message_text', 'barber_name_1'), reply_markup=inline_keyboard)
            await state.set_state(UserState.barber_name)


    except Exception as e:
        print(f"Error:{e}")



@router.message(UserState.barber_name)
async def check_barber_name(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        data = await state.get_data()
        lang = data['language']
        if message.text == get_text(lang, "buttons", "back"):
            await message.answer(text=get_text(lang, 'message_text', 'menu'), reply_markup=kb.menu(lang))
            await state.set_state(UserState.menu)

        if message.text in {"Ali":"Ali","Ismoil":"Ismoil","Bobur":"Bobur","Shoxruh":"Shoxruh"}:
            await state.update_data(barber_name=message.text)
            await message.answer(text=get_text(lang, 'message_text', 'select_date'), reply_markup=kb.today_or_another(lang))
            await state.set_state(UserState.select_date)

    except Exception as e:
        print(f"Error:{e}")


@router.message(UserState.select_date)
async def check_select_date(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        data = await state.get_data()
        lang = data['language']


        if message.text == get_text(lang, "buttons", "back"):
            await message.answer(text=get_text(lang, 'message_text', 'barber_name'), reply_markup=kb.barber_name(lang))
            await state.set_state(UserState.barber_name)


        if message.text == get_text(lang, "buttons", "today"):
            await state.update_data(select_date=message.text.split(" ")[1])
            await message.answer(text=get_text(lang, 'message_text', 'select_time'), reply_markup=kb.select_time(lang))
            await state.set_state(UserState.select_time)

        if message.text == get_text(lang, "buttons", "another_day"):
            await message.answer(text=get_text(lang, 'message_text', 'sana'), reply_markup=kb.select_date(lang))
            await state.set_state(UserState.sana)

    except Exception as e:
        print(f"Error:{e}")


@router.message(UserState.sana)
async def check_sana(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        data = await state.get_data()
        lang = data['language']
        if message.text in ["05-08-2025","06-08-2025","07-08-2025","08-08-2025"]:
            await state.update_data(select_date=message.text)
            await message.answer(text=get_text(lang, 'message_text', 'select_time'), reply_markup=kb.select_time(lang))
            await state.set_state(UserState.select_time)

    except Exception as e:
        print(f"Error:{e}")


@router.message(UserState.select_time)
async def check_select_time(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        data = await state.get_data()
        lang = data['language']

        if message.text == get_text(lang, "buttons", "back"):
            await message.answer(text=get_text(lang, 'message_text', 'select_date'), reply_markup=kb.select_date(lang))
            await state.set_state(UserState.select_date)


        if message.text in ["10:00","10:30","11:00","11:30","12:00","12:30"]:
            await state.update_data(select_time=message.text)

            msg_text = (
                f"{get_text(lang, 'message_text', 'confirmed_userinfo')}\n"
                f"{get_text(lang, 'message_text', 'conf_barber_name')} {data["barber_name"]}\n\n"
                f"{get_text(lang, 'message_text', 'conf_day')} {data["select_date"]}\n\n"
                f"{get_text(lang, 'message_text', 'service_types')} {data["service_type"]}\n\n"
                f"{get_text(lang, 'message_text', 'conf_time')} {message.text}\n"
            )

            await bot.send_message(chat_id=user_id, text=msg_text, reply_markup=kb.conf_booking(lang))
            await state.set_state(UserState.conf_book_and_payment)

    except Exception as e:
        print(f"Error:{e}")




@router.message(UserState.conf_book_and_payment)
async def conf_book_and_payment(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        data = await state.get_data()
        lang = data['language']
        if message.text == get_text(lang, "buttons", "back"):
            await message.answer(text=get_text(lang, 'message_text', 'select_time'), reply_markup=kb.select_time(lang))
            await state.set_state(UserState.select_time)

        if message.text == get_text(lang, "buttons", "rejected"):
            await message.answer(text=get_text(lang, 'message_text', 'menu'), reply_markup=kb.menu(lang))
            await state.set_state(UserState.menu)

        if message.text == get_text(lang, "buttons", "confirm"):
            await message.answer(text=get_text(lang, 'message_text', 'payment'), reply_markup=kb.payment(lang))
            await state.set_state(UserState.payment)
            await state.set_state(UserState.check_payment)

    except Exception as e:
        print(f"Error:{e}")


@router.message(UserState.check_payment)
async def check_payment(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        data = await state.get_data()
        lang = data['language']
        if message.text == get_text(lang, "buttons", "Click"):
            await bot.send_invoice(
                chat_id=message.chat.id,
                title="Barber uchun to'lov",
                description="Barber uchun to'lov",
                payload="k_001",
                provider_token=config('PROVIDER_TOKEN'),
                currency="UZS",
                prices=[LabeledPrice(label="1 marttalik to'lov", amount=1000000 * 10)],  # 10,000 so'm
                start_parameter="time-machine-example",
                need_name=False,
                need_phone_number=True,
                need_email=False,
                is_flexible=False
            )
    except Exception as e:
        print(f"Error:{e}")



@dp.pre_checkout_query(lambda query: True)
async def pre_checkout_query_handler(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)



@dp.message(F.successful_payment)
async def successful_payment_handler(message: Message):
    user_id = message.from_user.id
    amount = message.successful_payment.total_amount // 100
    currency = message.successful_payment.currency

    await message.answer(f"✅ To‘lov muvaffaqiyatli bajarildi! {amount} {currency} uchun rahmat 🙌")








