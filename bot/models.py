from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    date = Column(String)
    time = Column(String)
    price = Column(String)
    description = Column(String)

    def __repr__(self):
        return f"Event(id={self.id}, name={self.name}, date={self.date}, time={self.time}, price={self.price})"


class Person(Base):
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True)
    language = Column(String)
    name = Column(String, nullable=True)
    phone = Column(String, nullable=True)

    def __repr__(self):
        return f"Person(id={self.id}, name={self.name}, phone={self.phone})"
