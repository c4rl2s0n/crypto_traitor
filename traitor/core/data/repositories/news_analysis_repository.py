from datetime import datetime
from typing import List
from dependency_injector.wiring import inject, Provide
from traitor.core.data.db import Database
from traitor.core.data.models import Article, CoinNewsSummary, SummaryTimeframe
from traitor.core.data.repositories import Repository


class NewsAnalysisRepository(Repository):
    
    def __init__(self):
        super().__init__(model=CoinNewsSummary)
    
    def get_latest_for_coin(self, coin_id: int, timeframe: SummaryTimeframe = SummaryTimeframe.WEEK) -> CoinNewsSummary:
        return self.db.session.query(CoinNewsSummary).filter_by(
            coin_id=coin_id, 
            timeframe=timeframe
        ).order_by(CoinNewsSummary.date_generated.desc()).first()