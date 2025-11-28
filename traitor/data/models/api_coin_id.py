from traitor.data import Base
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Index


class ApiCoinID(Base):
    __tablename__ = 'api_coin_ids'

    id = Column(Integer, primary_key=True, autoincrement=True)
    coin_id = Column(Integer, ForeignKey(f"coins.id"), index=True, back_populates="apis")
    api_name = Column(String, index=True)
    api_coin_id = Column(String)

    @staticmethod
    def setup_indices():
        Index("ix_api_coin", ApiCoinID.api_coin_id, ApiCoinID.coin_id)
        pass

