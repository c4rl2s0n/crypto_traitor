from abc import ABC
from typing import TypeVar, Generic, Type

from dependency_injector.wiring import inject, Provide
from sqlalchemy import select

from traitor.core.data.db import Database

T = TypeVar("T")

class Repository(ABC, Generic[T]):

    @inject
    def __init__(self, model: Type[T], db: Database = Provide["db"]):
        self.model = model
        self.db = db


    def update(self, entity: T):
        with self.db.write_session() as s:
            s.merge(entity)

    def update_all(self, entities: list[T]):
        with self.db.write_session() as s:
            [s.merge(e) for e in entities]

    def add(self, entity: T):
        with self.db.write_session() as s:
            s.add(entity)

    def add_all(self, entities: list[T]):
        with self.db.write_session() as s:
            s.add_all(entities)

    def empty(self) -> bool:
        with self.db.read_session() as s:
            exists = select(s.query(self.model).exists())
            return not s.execute(exists).scalar()

    def get_all(self) -> list[T]:
        with self.db.read_session() as s:
            return s.query(self.model).all()
