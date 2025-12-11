from sqlalchemy import Column, DateTime, Integer, String

from traitor.core.data import Base


class TokenUsage(Base):
    __tablename__ = "token_usage"

    time = Column(DateTime(timezone=True), nullable=False, primary_key=True)
    id = Column(Integer, primary_key=True, autoincrement=True)
    input_tokens = Column(Integer, nullable=False)
    cached_tokens = Column(Integer, nullable=False)
    output_tokens = Column(Integer, nullable=False)
    reasoning_tokens = Column(Integer, nullable=True)
    tool_tokens = Column(Integer, nullable=True)
    api = Column(String)
    model = Column(String)
    comment = Column(String, nullable=True)
