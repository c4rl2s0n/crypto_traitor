from sqlalchemy import desc

from traitor.core.data.models import TradingStrategy, TokenUsage
from traitor.core.data.repositories.repository import Repository


class TokenUsageRepository(Repository):
    def __init__(self):
        super().__init__(model=TokenUsage)

