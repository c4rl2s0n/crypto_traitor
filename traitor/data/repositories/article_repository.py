from typing import List

from dependency_injector.wiring import inject, Provide
from sqlalchemy import or_

from traitor.data.db import Database
from traitor.data.models.article import Article


class ArticleRepository(object):
    @inject
    def __init__(self, db: Database = Provide["db"]):
        self.db = db

    def add(self, article: Article):
        self.db.session.add(article)
        self.db.session.commit()

    def add_all(self, articles: List[Article]):
        self.db.session.add_all(articles)
        self.db.session.commit()

    def url_exists(self, url: str) -> bool:
        return self.db.session.query(Article).filter_by(url=url).first() is not None

    def get_without_summary(self) -> List[Article]:
        return self.db.session.query(Article).filter(
            or_(
                Article.summary.is_(None),
                Article.summary == ""
            )
        ).all()

    def commit(self):
        self.db.session.commit()