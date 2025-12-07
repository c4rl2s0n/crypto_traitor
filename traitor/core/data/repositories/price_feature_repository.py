from datetime import datetime
import pandas as pd
from dependency_injector.wiring import inject, Provide

from sqlalchemy import text, and_, or_, delete

from traitor.core.config import DBViews
from traitor.core.data.db import Database
from traitor.core.data.models import Price, PriceFeature, PriceFeatureInterval
from traitor.core.data.repositories.repository import Repository


class PriceFeatureRepository(Repository):

    def __init__(self):
        super().__init__(model=PriceFeature)

    def get_features(self, coin_id: int) -> dict[PriceFeatureInterval, PriceFeature]:
        with self.db.read_session() as s:
            result = s.query(self.model).filter(PriceFeature.coin_id == coin_id).all()
            return {row.interval:row for row in result}

    def clear(self):
        """
        Delete all the features
        :return:
        """
        with self.db.write_session() as s:
            stmt = delete(PriceFeature)
            s.execute(stmt)
