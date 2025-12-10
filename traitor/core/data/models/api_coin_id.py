import enum

from traitor.core.data import Base
from sqlalchemy import Column, String, Integer, ForeignKey, Index, Enum



class CoinApiType(enum.Enum):
    INFO = "info"
    EXCHANGE = "exchange"

class ApiCoinID(Base):
    __tablename__ = 'api_coin_ids'

    id = Column(Integer, primary_key=True, autoincrement=True)
    coin_id = Column(Integer, ForeignKey(f"coins.id", ondelete="CASCADE"), index=True)
    api_name = Column(String, index=True)
    api_coin_id = Column(String)
    api_type = Column(Enum(CoinApiType))

    @staticmethod
    def setup_indices():
        Index("ix_api_coin", ApiCoinID.api_coin_id, ApiCoinID.coin_id)
        pass

