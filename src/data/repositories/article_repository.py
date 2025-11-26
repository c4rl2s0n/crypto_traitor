from typing import List

from sqlalchemy import or_

from src.data.db import Database
from src.data.models.article import Article


class ArticleRepository(object):

    def __init__(self, db: Database):
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