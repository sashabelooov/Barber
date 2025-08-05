from aiogram.types import KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
import json



with open("data.json", "r", encoding="utf-8") as file:
    translations = json.load(file)

def get_text(lang, category, key):
    return translations.get(lang, {}).get(category, {}).get(key, f"[{key}]")

def start_key():
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text=f"🇺🇸 eng"), KeyboardButton(text=f"🇺🇿 uz"),KeyboardButton(text=f"🇷🇺 ru"))
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
    keyboard.add(
                 KeyboardButton(text=get_text(lang, 'buttons', 'back')))
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
    keyboard.add(KeyboardButton(text=get_text(lang, 'buttons', 'eng')), KeyboardButton(text=get_text(lang, 'buttons', 'uz')),
                 KeyboardButton(text=get_text(lang, 'buttons', 'ru')),KeyboardButton(text=get_text(lang, 'buttons', 'back')))
    keyboard.adjust(3)
    return keyboard.as_markup(resize_keyboard=True)



def barber_name(lang):
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text="Ali"), KeyboardButton(text="Ismoil"),
                         KeyboardButton(text="Bobur"),KeyboardButton(text="Shoxruh"),
                 KeyboardButton(text=get_text(lang, 'buttons', 'back')))
    keyboard.adjust(2)
    return keyboard.as_markup(resize_keyboard=True)


def today_or_another(lang):
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text=get_text(lang, 'buttons', 'today')),
                 KeyboardButton(text=get_text(lang, 'buttons', 'another_day')),
                 KeyboardButton(text=get_text(lang, 'buttons', 'back')))
    keyboard.adjust(2)
    return keyboard.as_markup(resize_keyboard=True)


def select_date(lang):
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text='05-08-2025'),KeyboardButton(text='06-08-2025'),
                 KeyboardButton(text='07-08-2025'),KeyboardButton(text='08-08-2025'),
                 KeyboardButton(text=get_text(lang, 'buttons', 'back')))
    keyboard.adjust(2)
    return keyboard.as_markup(resize_keyboard=True)



def select_time(lang):
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text='10:00'),KeyboardButton(text='10:30'),
                 KeyboardButton(text='11:00'),KeyboardButton(text='10:30'),
                 KeyboardButton(text=get_text(lang, 'buttons', 'back')))
    keyboard.adjust(2)
    return keyboard.as_markup(resize_keyboard=True)


def conf_booking(lang):
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text=get_text(lang, 'buttons', 'confirm')), KeyboardButton(text=get_text(lang, 'buttons', 'rejected')),
                 KeyboardButton(text=get_text(lang, 'buttons', 'back')))
    keyboard.adjust(2)
    return keyboard.as_markup(resize_keyboard=True)







def service_type(lang):
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text=get_text(lang, 'buttons', 'hair')),
                 KeyboardButton(text=get_text(lang, 'buttons', 'hair_beard')),
                 KeyboardButton(text=get_text(lang, 'buttons', 'back')))
    keyboard.adjust(2)
    return keyboard.as_markup(resize_keyboard=True)




def payment(lang):
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text=get_text(lang, 'buttons', 'Click')), KeyboardButton(text=get_text(lang, 'buttons', 'Payme')))
    keyboard.adjust(2)
    return keyboard.as_markup(resize_keyboard=True)









