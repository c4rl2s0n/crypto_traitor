from sqlalchemy import Column, Integer, DateTime, String

from traitor.core.data import Base

class PriceAnalysis(Base):
    __tablename__ = "price_analysis"

    coin_id = Column(Integer, primary_key=True)
    time = Column(DateTime, primary_key=True, nullable=True)
    analysis = Column(String)

