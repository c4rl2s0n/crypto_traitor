from datetime import datetime
import pandas as pd
from dependency_injector.wiring import inject, Provide

from sqlalchemy import text, and_, or_

from traitor.core.config import DBViews
from traitor.core.data.db import Database
from traitor.core.data.models import Price, PriceFeature, PriceFeatureInterval, PriceAnalysis
from traitor.core.data.repositories.repository import Repository


class PriceAnalysisRepository(Repository):

    def __init__(self):
        super().__init__(model=PriceAnalysis)

    def get_for_coin(self, coin_id: int) -> PriceAnalysis:
        with self.db.read_session() as s:
            result = s.query(self.model).filter(PriceAnalysis.coin_id == coin_id).all()
            return [row for row in result][0]
        
    def get_latest_for_coin(self, coin_id: int) -> PriceAnalysis:
        return self.db.session.query(PriceAnalysis).filter_by(
            coin_id=coin_id
        ).order_by(PriceAnalysis.time.desc()).first()
