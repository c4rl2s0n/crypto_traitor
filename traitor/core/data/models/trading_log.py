from sqlalchemy import Column, DateTime, Integer, String, Float

from traitor.core.data import Base


class TradingLog(Base):
    __tablename__ = "trading_logs"

    time = Column(DateTime(timezone=True), nullable=False, primary_key=True)
    id = Column(Integer, primary_key=True, autoincrement=True)
    coin_out_id = Column(Integer, nullable=False)
    coin_out_name = Column(String, nullable=False)
    coin_in_id = Column(Integer, nullable=False)
    coin_in_name = Column(String, nullable=False)
    balance_out = Column(Float, nullable=False)
    balance_in = Column(Float, nullable=True)
    coin_out_value = Column(Float, nullable=True)
    coin_in_value = Column(Float, nullable=True)
    comment = Column(String, nullable=True)

    def to_string(self) -> str:
        return f"[{self.time}] {self.balance_out} {self.coin_out_name} ({self.coin_out_value}) <--> {self.balance_in} {self.coin_in_name} ({self.coin_in_value})"