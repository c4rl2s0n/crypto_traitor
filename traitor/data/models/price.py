from sqlalchemy import Column, DateTime, Float, String, Integer

from traitor.data import Base


class Price(Base):
    __tablename__ = "prices"

    time = Column(DateTime(timezone=True), nullable=False, primary_key=True)
    value = Column(Float, nullable=False)
    coin_id = Column(Integer, primary_key=True)
    coin_symbol = Column(String)
    market_cap = Column(Float)
    trading_vol_24h = Column(Float)
    value_change_24h = Column(Float)
    #
    # def __init__(self,
    #              coin_id: str,
    #              coin_symbol: str,
    #              time: datetime,
    #              value: float,
    #              market_cap: float,
    #              trading_vol_24h: float,
    #              value_change_24h: float):
    #     self.time = time
    #     self.value = value
    #     self.coin_id = coin_id
    #     self.coin_symbol = coin_symbol
    #     self.market_cap = market_cap
    #     self.trading_vol_24h = trading_vol_24h
    #     self.value_change_24h = value_change_24h

