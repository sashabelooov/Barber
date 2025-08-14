from aiogram.types import KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
import json

from api import all_barbers_info, user_booking_history, barber_service_type, choosed_service

with open("data.json", "r", encoding="utf-8") as file:
    translations = json.load(file)

def get_text(lang, category, key):
    return translations.get(lang, {}).get(category, {}).get(key, f"[{key}]")

def start_key():
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text=f"🇺🇿 uz"), KeyboardButton(text=f"🇷🇺 ru"))
    keyboard.adjust(3)
    return keyboard.as_markup(resize_keyboard=True)


def ask_phone(lang):
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text=get_text(lang, 'buttons', 'contact'),request_contact=True))
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)



def conf(lang):
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text=get_text(lang, 'buttons', 'confirm')), KeyboardButton(text=get_text(lang, 'buttons', 'rejected')))
    keyboard.adjust(2)
    return keyboard.as_markup(resize_keyboard=True)


def back(lang):
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text=get_text(lang, 'buttons', 'back')))
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)



def menu(lang):
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text=get_text(lang, 'buttons', 'booking')), KeyboardButton(text=get_text(lang, 'buttons', 'booking_history')),
                 KeyboardButton(text=get_text(lang, 'buttons', 'contact_menu')),KeyboardButton(text=get_text(lang, 'buttons', 'location')),
                 KeyboardButton(text=get_text(lang, 'buttons', 'price_list')),KeyboardButton(text=get_text(lang, 'buttons', 'change_lang')))
    keyboard.adjust(2,2,1)
    return keyboard.as_markup(resize_keyboard=True)


def language(lang):
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text=get_text(lang, 'buttons', 'uz')),
                 KeyboardButton(text=get_text(lang, 'buttons', 'ru')),
                 KeyboardButton(text=get_text(lang, 'buttons', 'back')))
    keyboard.adjust(2,1)
    return keyboard.as_markup(resize_keyboard=True)


barber_with_telegramid = {}
async def barber_name(lang):
    keyboard = ReplyKeyboardBuilder()
    names = await all_barbers_info(1)
    for i in names:
        barber_with_telegramid[i["first_name"]] = i["telegram_id"]
        keyboard.add(KeyboardButton(text=f'{i["first_name"]}'))
    keyboard.add(KeyboardButton(text=get_text(lang, 'buttons', 'back')))
    keyboard.adjust(2,1)
    return keyboard.as_markup(resize_keyboard=True)


async def booking_history(lang, tg_id):
    keyboard = ReplyKeyboardBuilder()
    booking_hist = await user_booking_history(tg_id)
    if not booking_hist:
        keyboard.add(KeyboardButton(text=get_text(lang, 'buttons', 'back')))
    else:
        for i in booking_hist:
            keyboard.add(KeyboardButton(text=f"{i["start_time"]}"))
        KeyboardButton(text=get_text(lang, 'buttons', 'back'))
    keyboard.adjust(2)
    return keyboard.as_markup(resize_keyboard=True)


selected_service = {}
async def services(lang, tg_id):
    keyboard = ReplyKeyboardBuilder()
    service_type_barber = await barber_service_type(tg_id)
    for i in service_type_barber:
        for k,v in i.items():
            if k == 'name':
                keyboard.add(KeyboardButton(text=f"{v}"))
                selected_service[i["name"]] = i["id"]
    keyboard.add(KeyboardButton(text=get_text(lang, 'buttons', 'back')))
    keyboard.adjust(2, 1)
    return keyboard.as_markup(resize_keyboard=True)

check_selected_types = []
async def type_of_selected_service(lang, barber_id):
    keyboard = ReplyKeyboardBuilder()
    servicetypes = await choosed_service(barber_id)
    for i in servicetypes:
        for k,v in i.items():
            if k == "name":
                keyboard.add(KeyboardButton(text=f'{v}'))
                check_selected_types.append(v)
    print(check_selected_types)
    keyboard.add(KeyboardButton(text=get_text(lang, 'buttons', 'back')))
    keyboard.adjust(2,1)
    return keyboard.as_markup(resize_keyboard=True)



async def date(lang):
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text=get_text(lang, 'buttons', 'today')),
                 KeyboardButton(text=get_text(lang, 'buttons', 'another_day')))
    keyboard.add(KeyboardButton(text=get_text(lang, 'buttons', 'back')))
    keyboard.adjust(2,1)
    return keyboard.as_markup(resize_keyboard=True)