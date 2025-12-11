from traitor.core.data.models import TradingLog
from traitor.core.data.repositories.repository import Repository


class TradingLogRepository(Repository):
    def __init__(self):
        super().__init__(model=TradingLog)

    def get_latest(self, count: int = 1) -> list[TradingLog]:
        if count <= 0:
            return []
        with self.db.read_session() as s:
            return s.query(TradingLog).order_by(TradingLog.time.desc()).limit(count).all()
