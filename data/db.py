from sqlalchemy import create_engine, Index
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class Database(object):
    def __init__(self, path: str):
        self.engine = create_engine(f'sqlite:///{path}', echo=True)
        self._prepare_database()
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.session = self.SessionLocal()

    def _prepare_database(self):
        # important for SQLAlchemy to correctly register the models!
        from data.models import Article, Coin
        Index("idx_article_has_summary", Article.summary)

        Base.metadata.create_all(self.engine)

    def close(self):
        self.session.close()
