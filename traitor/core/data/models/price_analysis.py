from sqlalchemy import Column, Integer, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship

from traitor.core.data import Base

class PriceAnalysis(Base):
    __tablename__ = "price_analysis"

    coin_id = Column(Integer, ForeignKey('coins.id', ondelete="CASCADE"), primary_key=True)
    time = Column(DateTime, primary_key=True, nullable=True)
    analysis = Column(String)


