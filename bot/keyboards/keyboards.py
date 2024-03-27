import os

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from bot.models import Event
from bot.texts.text_manager import ButtonText, translate


def language_choice() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Українська 🇺🇦")
    kb.button(text="English 🇬🇧")
    kb.button(text="Русский 🇷🇺")
    return kb.as_markup(resize_keyboard=True, one_time_keyboard=True)


def event_choice(event: Event, lang_code: str) -> InlineKeyboardMarkup:
    sign_up_button = InlineKeyboardButton(
        text=translate(ButtonText.register, lang=lang_code),
        callback_data=f"register_{event.id}",
    )
    info_button = InlineKeyboardButton(
        text=translate(ButtonText.info, lang=lang_code),
        url=event.description,
        callback_data=f"info_{event.id}",
    )
    builder = InlineKeyboardBuilder()
    builder.row(sign_up_button, info_button)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def payment_choice(lang_code: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=translate(ButtonText.pay_50, lang=lang_code), callback_data="pay_50")
    kb.button(text=translate(ButtonText.pay_100, lang=lang_code), callback_data="pay_100")
    return kb.as_markup(resize_keyboard=True, one_time_keyboard=True)


def approve_payment() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Підтвердити", callback_data="approve")
    kb.button(text="Відхилити", callback_data="decline")
    return kb.as_markup(resize_keyboard=True, one_time_keyboard=True)


def main_menu_keyboard(lang_code: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text=translate(ButtonText.text_me, lang=lang_code),
        url=os.getenv("OWNER_LINK"),
        callback_data="text_me",
    )
    kb.button(
        text=translate(ButtonText.show_events, lang=lang_code),
        callback_data="show_events",
    )
    return kb.as_markup(resize_keyboard=True, one_time_keyboard=True)


def image_sent() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text=translate(ButtonText.ok, lang="ua"))
    return kb.as_markup(resize_keyboard=True, one_time_keyboard=True)
