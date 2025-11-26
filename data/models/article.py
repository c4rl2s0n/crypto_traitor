from sqlalchemy.ext.hybrid import hybrid_property

from data.db import Base
from sqlalchemy import Column, String, DATE, case


class Article(Base):
    __tablename__ = 'articles'

    url = Column(String, primary_key=True)
    category = Column(String)
    title = Column(String)
    date_published = Column(DATE)
    content = Column(String)
    summary = Column(String, nullable=True)

    @property
    def has_summary(self):
        return bool(self.summary and self.summary.strip())

    def __str__(self):
        return f"""
Source: {self.url}
Published: {self.date_published} 
Title: '{self.title}'
Category: '{self.category}'

Content:
{self.content}""".strip()
