from aiogram.fsm.state import State, StatesGroup


class States(StatesGroup):
    event_choice = State()
    language_choice = State()
    enter_name = State()
    enter_phone = State()
    calculate_amount = State()
    receipt_request = State()
    sign_up_request = State()
    main_menu = State()
