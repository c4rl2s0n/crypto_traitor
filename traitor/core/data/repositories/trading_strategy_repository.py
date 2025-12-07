from sqlalchemy import or_, desc

from traitor.core.data.models import TradingStrategy
from traitor.core.data.models.article import Article
from traitor.core.data.repositories.repository import Repository


class TradingStrategyRepository(Repository):
    def __init__(self):
        super().__init__(model=TradingStrategy)

    def get_latest(self) -> TradingStrategy | None:
        with self.db.read_session() as s:
            result = s.query(TradingStrategy).order_by(desc(TradingStrategy.time)).limit(1).all()
            if len(result) == 0:
                return None
            return result[0]
