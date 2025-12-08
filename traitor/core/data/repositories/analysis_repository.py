from datetime import datetime
from typing import List
from dependency_injector.wiring import inject, Provide
from traitor.core.data.db import Database
from traitor.core.data.models import Article, CoinSummary

class AnalysisRepository:
    @inject
    def __init__(self, db: Database = Provide["db"]):
        self.db = db

    def add(self, summary: CoinSummary):
        self.db.session.add(summary)
        self.db.session.commit()

    def get_articles_in_range(self, start_date: datetime) -> List[Article]:
        return self.db.session.query(Article).filter(
            Article.date_published >= start_date.date(),
            Article.summary.isnot(None),
            Article.summary != ""
        ).all()