from traitor.core.data import Base
from sqlalchemy import Column, String, Integer, DateTime

from traitor.core.tools.misc import time_to_str


class TradingStrategy(Base):
    __tablename__ = 'trading_strategies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    strategy = Column(String)
    reason = Column(String, nullable=True)
    time = Column(DateTime)

    def to_string(self, with_time: bool = True):
        s = f"Strategy: {self.strategy}"
        if self.reason is not None and len(self.reason) > 0:
            s += f"\nReason: {self.reason}"
        if with_time:
            s = f"[{time_to_str(self.time)}]\n{s}"
        return s