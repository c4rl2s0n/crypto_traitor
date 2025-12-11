from traitor.core.data.models import TradingLog
from traitor.core.data.repositories.repository import Repository


class TradingLogRepository(Repository):
    def __init__(self):
        super().__init__(model=TradingLog)

