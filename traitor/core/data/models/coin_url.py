from sqlalchemy import Column, String, Integer, ForeignKey

from traitor.core.data import Base


class CoinUrl(Base):
    __tablename__ = 'coin_urls'

    id = Column(Integer, primary_key=True, autoincrement=True)
    coin_id = Column(Integer, ForeignKey(f"coins.id", ondelete="CASCADE"), index=True)
    url = Column(String)
    description = Column(String, nullable=True)
