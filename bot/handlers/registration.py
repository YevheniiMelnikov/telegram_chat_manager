import asyncio
import os

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.handlers.routers import registration_router
from bot.keyboards.keyboards import payment_choice, image_sent, main_menu_keyboard
from bot.states import States
from bot.texts.text_manager import MessageText, translate
from functions import edit_person, get_events, get_person_by_id, resend_receipt, stop_timer
from logger import logger
from settings import MIN_PRICE


@registration_router.callback_query(States.event_choice)
async def set_chosen_event(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(chosen_event=callback.data.split("_")[1])
    person = await get_person_by_id(callback.from_user.id)
    if person.name is None:
        await callback.message.answer(translate(MessageText.enter_name, lang=person.language))
        await state.set_state(States.enter_name)
    elif person.phone is None:
        await callback.message.answer(translate(MessageText.share_contact, lang=person.language))
        await state.set_state(States.enter_phone)
    else:
        await callback.message.answer(
            translate(MessageText.choose_payment_type, lang=person.language),
            reply_markup=payment_choice(person.language),
        )
        await state.set_state(States.calculate_amount)


@registration_router.message(States.enter_name)
async def set_user_name(message: Message, state: FSMContext) -> None:
    person = await get_person_by_id(message.from_user.id)
    await edit_person(person.id, {"name": message.text})
    await state.update_data(person=person)
    await state.set_state(States.enter_phone)
    await message.answer(translate(MessageText.share_contact, lang=person.language))


@registration_router.message(States.enter_phone)
async def set_user_phone(message: Message, state: FSMContext) -> None:
    person = await get_person_by_id(message.from_user.id)
    await edit_person(person.id, {"phone": message.text})
    await state.update_data(person=person)
    await message.answer(translate(MessageText.user_created, lang=person.language))
    await message.answer(
        translate(MessageText.choose_payment_type, lang=person.language),
        reply_markup=payment_choice(person.language),
    )
    await state.set_state(States.calculate_amount)


@registration_router.callback_query(States.calculate_amount)
async def calculate_amount(callback: CallbackQuery, state: FSMContext):
    try:
        person = await get_person_by_id(callback.from_user.id)
        payment_type = None

        match callback.data:
            case "pay_50":
                payment_type = 0.5
            case "pay_100":
                payment_type = 1

        if payment_type is not None:
            data = await state.get_data()
            chosen_event_id = int(data.get("chosen_event"))

            events = await get_events()
            chosen_event = next((event for event in events if event.id == chosen_event_id), None)

            if chosen_event:
                if chosen_event.price is None:
                    amount = int(MIN_PRICE * payment_type)
                else:
                    price = int(chosen_event.price)
                    amount = int(price * payment_type)

                logger.info(f"User {person.id} ready to pay {amount} UAH for {chosen_event.name}")
                await callback.message.answer(
                    translate(MessageText.make_payment, lang=person.language).format(
                        amount=amount, card=os.getenv("BANK_CARD")
                    )
                )
                await state.update_data(amount=amount, event=chosen_event.name, date=chosen_event.date)
            await state.set_state(States.receipt_request)

    except Exception as e:
        logger.exception(f"An error occurred: {e}")


@registration_router.message(States.receipt_request)
async def receipt_request(message: Message, state: FSMContext) -> None:
    person = await get_person_by_id(message.from_user.id)
    if message.photo:
        logger.info(f"User {person.id} sent an image")
        await state.set_state(States.wait_for_approve)
        await message.answer(translate(MessageText.successful_registration, lang=person.language), reply_markup=image_sent())
        await asyncio.create_task(stop_timer(person.id))
        await asyncio.create_task(resend_receipt(message, state))
    else:
        await message.answer(translate(MessageText.wrong_format, lang=person.language))
        await message.delete()
        await state.set_state(States.receipt_request)


@registration_router.message(States.wait_for_approve)
async def wait_for_approve(message: Message, state: FSMContext) -> None:
    person = await get_person_by_id(message.from_user.id)
    await state.set_state(States.main_menu)
    await message.answer(translate(MessageText.start, lang=person.language), reply_markup=main_menu_keyboard(person.language))
    await message.delete()


@registration_router.message(States.event_choice)
async def message_in_event_choice(message: Message, state: FSMContext) -> None:
    await message.delete()
    await state.set_state(States.event_choice)
