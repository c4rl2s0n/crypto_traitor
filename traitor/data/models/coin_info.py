from traitor.data import Base
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey


class CoinInfo(Base):
    __tablename__ = 'coin_infos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    coin_id = Column(Integer, ForeignKey(f"coins.id"), index=True)
    url = Column(String)
    description = Column(String, nullable=True)
