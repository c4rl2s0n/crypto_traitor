from sqlalchemy.ext.hybrid import hybrid_property

from data.db import Base
from sqlalchemy import Column, String, Boolean


class Coin(Base):
    __tablename__ = 'coins'

    tag = Column(String, primary_key=True)
    name = Column(String)
    description = Column(String, nullable=True)
    url_coinmarketcap = Column(String, nullable=True)
    active = Column(Boolean, default=False)
