from sqlalchemy import Column, String, Boolean, Integer, ForeignKey

from traitor.data import Base


class CoinURL(Base):
    __tablename__ = 'coin_urls'

    id = Column(Integer, primary_key=True, autoincrement=True)
    coin_id = Column(Integer, ForeignKey(f"coins.id"), index=True, back_populates="urls")
    url = Column(String)
    description = Column(String, nullable=True)
