import logging
from datetime import timedelta

from traitor.core.agents.agent_base import AgentBase
from traitor.core.research.news.news_source import NewsSource
from traitor.core.services import NewsResearchService
from traitor.core.tools import NewsSummarAIzer


class NewsResearchAgent(AgentBase):
    name = "News Research"
    interval = timedelta(hours=1)

    def __init__(self, sources: list[NewsSource]):
        self.sources = sources
        self.research_service = NewsResearchService(summarizer=NewsSummarAIzer())
        logging.info(f"Init NewsResearchAgent\n\tLLM: {self.research_service.summarizer.model}\n\tSources: {[s.name for s in sources]}")

    def _do_task(self):
        logging.info("Update news...")
        try:
            self.research_service.research_news(self.sources)
        except Exception as e:
            logging.exception("Error while researching...")
