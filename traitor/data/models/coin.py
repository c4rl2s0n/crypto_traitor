import uuid

from sqlalchemy.orm import relationship

from traitor.data import Base
from sqlalchemy import Column, String, Boolean, Integer

from traitor.data.models import ApiCoinID


class Coin(Base):
    __tablename__ = 'coins'

    # id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String)
    name = Column(String)
    description = Column(String, nullable=True)
    active = Column(Boolean, default=False)
    apis = relationship("ApiCoinID")
    urls = relationship("CoinURL")

    def get_api(self, name: str) -> ApiCoinID | None:
        for api in self.apis:
            if api.api_name == name:
                return api
        return None
