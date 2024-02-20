from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.keyboards import language_choice, main_menu_keyboard
from bot.states import States
from bot.texts.text_manager import MessageText, translate
from functions import add_user_to_db, edit_person, get_person_by_id, show_all_events

start_router = Router()


@start_router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    person = await get_person_by_id(message.from_user.id)
    if person:
        await state.set_state(States.main_menu)
        await message.answer(
            text=translate(MessageText.start, lang=person.language),
            reply_markup=main_menu_keyboard(person.language),
        )
    else:
        await message.answer(
            text=translate(MessageText.choose_language), reply_markup=language_choice()
        )
        await state.set_state(States.language_choice)


@start_router.message(States.language_choice)
async def create_user(message: Message, state: FSMContext) -> None:
    codes = {"Українська 🇺🇦": "ua", "English 🇬🇧": "eng", "Русский 🇷🇺": "ru"}
    lang_code = codes.get(message.text)

    if lang_code:
        person = await get_person_by_id(message.from_user.id)
        if person:
            await edit_person(message.from_user.id, {"language": lang_code})
        else:
            await add_user_to_db(user_id=message.from_user.id, lang=lang_code)
        await state.set_state(States.main_menu)
        await message.answer(
            text=translate(MessageText.start, lang=lang_code),
            reply_markup=main_menu_keyboard(lang_code),
        )
    else:
        await message.answer(
            text=translate(MessageText.choose_language), reply_markup=language_choice()
        )


@start_router.callback_query(States.main_menu)
async def main_menu(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.data == "show_events":
        person = await get_person_by_id(callback.from_user.id)
        if person:
            await show_all_events(callback.message, state, person)
            await state.set_state(States.event_choice)
        else:
            await state.set_state(States.main_menu)
    else:
        await state.set_state(States.main_menu)


@start_router.message(States.main_menu)
async def message_in_main_menu(message: Message, state: FSMContext) -> None:
    await message.delete()
    await state.set_state(States.main_menu)
    