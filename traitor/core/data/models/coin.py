from sqlalchemy.orm import relationship

from traitor.core.data import Base
from sqlalchemy import Column, String, Boolean, Integer, DateTime, Float

from traitor.core.data.models import ApiCoinID


class Coin(Base):
    __tablename__ = 'coins'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String)
    name = Column(String)

    description = Column(String, nullable=True)
    image = Column(String, nullable=True)
    genesis_date = Column(DateTime, nullable=True)
    block_time_in_minutes = Column(Float, nullable=True)
    initialized = Column(Boolean, default=False)

    active = Column(Boolean, default=False)
    apis = relationship("ApiCoinID")
    # urls = relationship("CoinUrl")
    # price_analyses = relationship("PriceAnalysis")
    # price_features = relationship("PriceFeature")
    # news_summaries = relationship("CoinNewsSummary")

    def get_api(self, name: str) -> ApiCoinID | None:
        for api in self.apis:
            if api.api_name == name:
                return api
        return None
