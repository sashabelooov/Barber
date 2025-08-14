import json
from aiogram import Bot, Dispatcher, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from decouple import config
from aiogram.enums import ChatAction
from aiogram import F
from aiogram.types import Message
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
            await bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
            await message.answer(text=get_text(lang, 'message_text', 'no_booking_history'), reply_markup=await kb.booking_history(lang, user_id))
            await state.set_state(UserState.booking_history)

        # ////////// Booking databaseda Isimlani obchiqish kerey \\\\\\\\\\\ #
        if message.text == get_text(lang, "buttons", "booking"):
            await bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
            await message.answer(text=get_text(lang, 'message_text', 'barber_name'), reply_markup=await kb.barber_name(lang))
            await state.set_state(UserState.barber_name)


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

        await state.update_data(language=message.text)  # 🌟 YANGILADI!
        await message.answer(text=get_text(message.text, 'message_text', 'menu'), reply_markup=kb.menu(message.text))
        await state.set_state(UserState.menu)

    except Exception as e:
        print(f"Error: {e}")




# ////////////////// booking_history \\\\\\\\\\\\\\\\\\\\\\\
@router.message(UserState.booking_history)
async def booking_history(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        data = await state.get_data()
        lang = data['language']
        if message.text == get_text(lang, "buttons", "back"):
            await message.answer(text=get_text(lang, 'message_text', 'menu'), reply_markup=kb.menu(lang))
            await state.set_state(UserState.menu)

    except Exception as e:
        print(f"Error:{e}")



# ////////////////// barber_name \\\\\\\\\\\\\\\\\\\\\\\
from keyboards import barber_with_telegramid, selected_service, check_selected_types
@router.message(UserState.barber_name)
async def barber_name(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        data = await state.get_data()
        lang = data['language']
        if message.text == get_text(lang, "buttons", "back"):
            await message.answer(text=get_text(lang, 'message_text', 'menu'), reply_markup=kb.menu(lang))
            await state.set_state(UserState.menu)
        elif message.text in barber_with_telegramid:
            await state.update_data(barber_name=message.text)
            barber_tg_id = barber_with_telegramid[message.text]
            await message.answer(text=get_text(lang, 'message_text', 'service_type'), reply_markup= await kb.services(lang,barber_tg_id))
            await state.set_state(UserState.check_service_type)
    except Exception as e:
        print(f"Error:{e}")



# ////////////////// check_service_type \\\\\\\\\\\\\\\\\\\\\\\
@router.message(UserState.check_service_type)
async def check_service_type(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        data = await state.get_data()
        lang = data['language']
        if message.text == get_text(lang, "buttons", "back"):
            await bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
            await message.answer(text=get_text(lang, 'message_text', 'barber_name'),reply_markup=await kb.barber_name(lang))
            await state.set_state(UserState.barber_name)
        elif message.text in selected_service:
            barber_id = selected_service[message.text]
            await state.update_data(selected_service=message.text)
            await bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
            await message.answer(text=get_text(lang, 'message_text', 'optionforservices'), reply_markup=await kb.type_of_selected_service(lang, barber_id))
            await state.set_state(UserState.type_of_selected_service)

    except Exception as e:
        print(f"Error:{e}")


# ////////////////// check_service_type \\\\\\\\\\\\\\\\\\\\\\\
@router.message(UserState.check_service_type)
async def check_service_type(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        data = await state.get_data()
        lang = data['language']
        if message.text == get_text(lang, "buttons", "back"):
            await bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
            await message.answer(text=get_text(lang, 'message_text', 'barber_name'),reply_markup=await kb.barber_name(lang))
            await state.set_state(UserState.barber_name)
        elif message.text in selected_service:
            barber_id = selected_service[message.text]
            await state.update_data(optionforservices=message.text)
            await bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
            await message.answer(text=get_text(lang, 'message_text', 'optionforservices'), reply_markup=await kb.type_of_selected_service(lang, barber_id))
            await state.set_state(UserState.select_date)

    except Exception as e:
        print(f"Error:{e}")



# ////////////////// select_date \\\\\\\\\\\\\\\\\\\\\\\
@router.message(UserState.select_date)
async def select_date(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        data = await state.get_data()
        lang = data['language']
        print(message.text)
        if message.text == get_text(lang, "buttons", "back"):
            barber_id = selected_service[message.text]
            await state.update_data(selected_service=message.text)
            await bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
            await message.answer(text=get_text(lang, 'message_text', 'optionforservices'),
                                 reply_markup=await kb.type_of_selected_service(lang, barber_id))
            await state.set_state(UserState.type_of_selected_service)

        if message.text in check_selected_types:
            await bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)
            await message.answer(text=get_text(lang, 'message_text', 'select_date'),reply_markup=await kb.date(lang))
            await state.set_state(UserState.selected_Date)

    except Exception as e:
        print(f"Error:{e}")