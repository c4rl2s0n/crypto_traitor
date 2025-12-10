from sqlalchemy import Column, DateTime, Float, String, Integer

from traitor.core.data import Base


class Price(Base):
    __tablename__ = "prices"

    time = Column(DateTime(timezone=True), nullable=False, primary_key=True)
    value = Column(Float, nullable=False)
    coin_id = Column(Integer, primary_key=True)
    coin_symbol = Column(String)
    market_cap = Column(Float)
    trading_vol_24h = Column(Float)
    value_change_24h = Column(Float)

