from typing import Any, List, Type

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import make_transient, sessionmaker

from bot.models import Base, Event, Person
from logger import logger
from settings import DB_NAME
from utils import singleton


@singleton
class Storage:
    def __init__(self):
        self.active_timers = set()
        self.engine = create_engine(url=DB_NAME)
        self.session = sessionmaker(bind=self.engine)()
        try:
            Base.metadata.create_all(self.engine)
        except Exception as e:
            logger.exception(f"An error occurred while creating tables: {e}")

    async def add_person(
        self,
        telegram_id: int,
        language_code: str,
        name: str | None = None,
        phone: str | None = None,
    ) -> None:
        try:
            person = Person(id=telegram_id, language=language_code, name=name, phone=phone)
            self.session.add(person)
            self.session.commit()
        except IntegrityError:
            self.session.rollback()

    async def edit_person(self, person_id: int, user_data: dict) -> bool:
        try:
            person = await self.get_person_by_id(person_id)
            for key, value in user_data.items():
                setattr(person, key, value)
            self.session.commit()
            return True
        except NoResultFound:
            logger.info(f"Person with id={person_id} not found")
            return False
        except IntegrityError:
            self.session.rollback()
            logger.warning(f"IntegrityError occurred while editing person with id={person_id}")
            return False

    async def get_person_by_id(self, person_id: int) -> Type[Person] | None:
        try:
            person = self.session.query(Person).filter_by(id=person_id).one()
            return person
        except NoResultFound:
            logger.info(f"Person with id={person_id} not found")
            return None

    async def get_all_events(self) -> list[Type[Event]] | list[Any]:
        try:
            events = self.session.query(Event).all()
            return events
        except Exception as e:
            logger.exception(f"An error occurred while getting all events: {e}")
            return []

    async def events_are_same(self, events: list[Event]) -> bool:
        return events == await self.get_all_events()

    async def update_events(self, events: List[Event]) -> None:
        if await self.events_are_same(events):
            return

        try:
            for event in events:
                make_transient(event)
            self.session.query(Event).delete()
            self.session.add_all(events)
            self.session.commit()
        except Exception as e:
            logger.exception(f"An error occurred while updating events: {e}")
            self.session.rollback()

    async def close(self) -> None:
        self.session.close()
