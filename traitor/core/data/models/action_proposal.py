from sqlalchemy import Column, Integer, Boolean, String, DateTime

from traitor.core.data import Base


class ActionProposal(Base):
    __tablename__ = "action_proposals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    done = Column(Boolean, default=False)
    time = Column(DateTime)
    proposal = Column(String)
    reason = Column(String, nullable=True)