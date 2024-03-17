from enum import Enum, auto

import yaml

import settings


class MessageText(Enum):
    start = auto()
    enter_name = auto()
    share_contact = auto()
    no_fixed_price = auto()
    wrong_format = auto()
    sign_up_approved = auto()
    sign_up_rejected = auto()
    make_payment = auto()
    approve_payment = auto()
    successful_registration = auto()
    choose_event = auto()
    event_data = auto()
    choose_language = auto()
    user_created = auto()
    choose_payment_type = auto()

    def __str__(self):
        return f"messages.{self.name}"


class ButtonText(Enum):
    share_contact = auto()
    register = auto()
    text_me = auto()
    info = auto()
    show_events = auto()
    pay_50 = auto()
    pay_100 = auto()

    def __str__(self):
        return f"buttons.{self.name}"


ResourceType = str | MessageText | ButtonText


class TextManager:
    def __init__(self):
        self.messages = self.load_messages()

    def get_text(self, key: ResourceType, lang: str | None = "eng") -> str | None:
        if str(key) in self.messages:
            return self.messages[str(key)][lang]
        else:
            raise ValueError(f"Key {key.name} not found in messages.yaml")

    @staticmethod
    def load_messages() -> dict:
        result = {}
        for type, path in settings.MESSAGES.items():
            with open(path, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)
            for key, value in data.items():
                result[f"{type}.{key}"] = value
        return result


resource_manager = TextManager()


def translate(key: ResourceType, lang: str | None = "ua") -> str:
    return resource_manager.get_text(key, lang)
