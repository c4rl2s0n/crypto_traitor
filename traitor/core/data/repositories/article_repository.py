from sqlalchemy import or_

from traitor.core.data.models.article import Article
from traitor.core.data.repositories.repository import Repository


class ArticleRepository(Repository):
    def __init__(self):
        super().__init__(model=Article)

    def url_exists(self, url: str) -> bool:
        with self.db.read_session() as s:
            return s.query(Article).filter_by(url=url).first() is not None

    def get_without_summary(self) -> list[Article]:
        with self.db.read_session() as s:
            return s.query(Article).filter(
                        or_(
                            Article.summary.is_(None),
                            Article.summary == ""
                        )
                    ).all()
