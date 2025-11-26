import uuid

from src.data.db import Base
from sqlalchemy import Column, String, Boolean


class Coin(Base):
    __tablename__ = 'coins'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    id_coingecko = Column(String, nullable=True)
    symbol = Column(String)
    name = Column(String)
    description = Column(String, nullable=True)
    active = Column(Boolean, default=False)
