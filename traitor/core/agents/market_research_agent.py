from traitor.core.agents.agent_base import AgentBase
from traitor.core.research.news.news_source import NewsSource


class MarketResearchAgent(AgentBase):

    def __init__(self, sources: list[NewsSource]):
        self.sources = sources
        self.research_service = None

    def _do_task(self):
        self.research_service.research_news(self.sources)
