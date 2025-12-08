from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from traitor.core.data import Base

class CoinSummary(Base):
    __tablename__ = 'coin_summaries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    coin_id = Column(Integer, ForeignKey('coins.id'), nullable=False)
    
    # '24h', '7d', '30d'
    timeframe = Column(String, nullable=False) 
    
    # El promedio matemático del sentimiento de los artículos analizados
    sentiment_score = Column(Float, nullable=True) 
    
    # El texto generado por la IA (El "Meta-Resumen")
    content = Column(Text, nullable=True)
    
    date_generated = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    coin = relationship("Coin", backref="summaries")

    def __repr__(self):
        return f"<CoinSummary(coin={self.coin_id}, frame={self.timeframe}, score={self.sentiment_score})>"