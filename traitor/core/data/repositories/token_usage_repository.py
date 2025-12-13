from traitor.core.data.models import TokenUsage
from traitor.core.data.repositories.repository import Repository


class TokenUsageRepository(Repository):
    def __init__(self):
        super().__init__(model=TokenUsage)

