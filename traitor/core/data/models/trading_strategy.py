from traitor.core.data import Base
from sqlalchemy import Column, String, DATE, Boolean, Computed, Integer, DateTime


class TradingStrategy(Base):
    __tablename__ = 'trading_strategies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    strategy = Column(String)
    reason = Column(String, nullable=True)
    time = Column(DateTime)