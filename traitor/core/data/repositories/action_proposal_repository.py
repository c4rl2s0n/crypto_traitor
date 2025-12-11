from traitor.core.data.models import TradingLog, ActionProposal
from traitor.core.data.repositories.repository import Repository


class ActionProposalRepository(Repository):
    def __init__(self):
        super().__init__(model=ActionProposal)

