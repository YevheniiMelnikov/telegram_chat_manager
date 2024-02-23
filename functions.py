import asyncio
from typing import Type

import aiohttp
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.keyboards.keyboards import approve_payment, event_choice
from bot.models import Event, Person
from bot.states import States
from bot.texts.text_manager import MessageText, ResourceType, TextManager, translate
from settings import (BOT_TOKEN, DB_NAME, GOOGLE_CREDENTIALS_FILE, OWNER_TG_ID,
                      SPREADSHEET_ID)
from sheets.sheets_manager import GoogleSheetsManager
from storage import Storage

storage = Storage(DB_NAME)


async def get_events() -> list[Event]:
    events = await storage.get_all_events()
    if events:
        return events

    sheets_manager = GoogleSheetsManager(SPREADSHEET_ID, GOOGLE_CREDENTIALS_FILE, storage)
    events = await sheets_manager.get_events()
    await storage.update_events(events)
    return events


async def manage_google_sheets() -> None:
    sheets_manager = GoogleSheetsManager(
        SPREADSHEET_ID, GOOGLE_CREDENTIALS_FILE, storage
    )
    updater_task = asyncio.create_task(sheets_manager.run())
    await updater_task


async def get_person_by_id(user_id: int) -> Type[Person] | None:
    return await storage.get_person_by_id(user_id)


async def add_user_to_db(
    user_id: int, lang: str, name: str | None = None, phone: str | None = None
) -> None:
    await storage.add_person(user_id, lang, name, phone)


async def edit_person(user_id: int, data: dict[str, str]) -> None:
    await storage.edit_person(user_id, data)


async def show_all_events(message: Message, state: FSMContext, person: Person) -> None:
    await message.answer(
        text=translate(MessageText.choose_event, lang=person.language),
        parse_mode="HTML",
    )
    for ev in await get_events():
        price_text = (
            ev.price
            if ev.price is not None
            else translate(MessageText.no_fixed_price, lang=person.language)
        )
        event_data = translate(MessageText.event_data, lang=person.language).format(
            name=ev.name, date=ev.date, time=ev.time, price=price_text
        )
        await message.answer(
            text=event_data,
            reply_markup=event_choice(ev, person.language),
            parse_mode="HTML",
        )
    await state.set_state(States.event_choice)


async def resend_receipt(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    person = await get_person_by_id(message.from_user.id)
    bot = Bot(BOT_TOKEN)
    async with aiohttp.ClientSession():
        await bot.send_photo(
            chat_id=OWNER_TG_ID,
            photo=message.photo[-1].file_id,
            caption=translate(MessageText.approve_payment).format(
                name=person.name,
                phone=person.phone,
                amount=data.get("amount"),
                event=data.get("event"),
                date=data.get("date"),
            ),
            reply_markup=approve_payment(),
            parse_mode="HTML",
        )
    await state.update_data(message=message)
    await state.set_state(States.sign_up_request)

