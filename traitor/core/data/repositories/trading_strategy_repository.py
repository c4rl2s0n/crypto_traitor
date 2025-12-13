from traitor.core.data.models import TradingStrategy
from traitor.core.data.repositories.repository import Repository


class TradingStrategyRepository(Repository):
    def __init__(self):
        super().__init__(model=TradingStrategy)

    def get_latest(self, count: int = 1) -> list[TradingStrategy]:
        if count <= 0:
            return []
        with self.db.read_session() as s:
            return s.query(TradingStrategy).order_by(TradingStrategy.time.desc()).limit(count).all()
