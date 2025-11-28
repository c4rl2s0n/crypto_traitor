from traitor.data import Base
from sqlalchemy import Column, String, DATE, Boolean, Computed


class Article(Base):
    __tablename__ = 'articles'

    url = Column(String, primary_key=True)
    category = Column(String)
    title = Column(String)
    date_published = Column(DATE)
    content = Column(String)
    summary = Column(String, nullable=True)
    has_summary = Column(
        Boolean,
        Computed("summary IS NOT NULL AND summary <> ''"),
        index=True
    )

    def __str__(self):
        return f"""
Source: {self.url}
Published: {self.date_published} 
Title: '{self.title}'
Category: '{self.category}'

Content:
{self.content}""".strip()
