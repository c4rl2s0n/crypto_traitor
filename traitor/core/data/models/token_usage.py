from sqlalchemy import Column, DateTime, Integer, String

from traitor.core.data import Base


class TokenUsage(Base):
    __tablename__ = "token_usage"

    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(DateTime(timezone=True), nullable=False)
    input_tokens = Column(Integer, nullable=False)
    cached_tokens = Column(Integer, nullable=False)
    output_tokens = Column(Integer, nullable=False)
    reasoning_tokens = Column(Integer, nullable=True)
    tool_tokens = Column(Integer, nullable=True)
    api = Column(String)
    model = Column(String)
    comment = Column(String, nullable=True)
